import os
import io
import json
import pickle

import pandas as pd
import shap

from flask import (
    Flask,
    request,
    jsonify,
    render_template,
    send_file
)

from dotenv import load_dotenv

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "model"
)

TEMPLATE_DIR = os.path.join(
    BASE_DIR,
    "templates"
)


# ============================================================
# ENV
# ============================================================

load_dotenv(
    os.path.join(
        BASE_DIR,
        ".env"
    )
)

PORT = int(
    os.getenv(
        "FLASK_PORT",
        "5000"
    )
)


# ============================================================
# FLASK
# ============================================================

app = Flask(
    __name__,
    template_folder=TEMPLATE_DIR
)


# ============================================================
# MODEL FILES
# ============================================================

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "model.pkl"
)

SCALER_PATH = os.path.join(
    MODEL_DIR,
    "scaler.pkl"
)

FEATURE_PATH = os.path.join(
    MODEL_DIR,
    "feature_columns.pkl"
)

LE_PATH = os.path.join(
    MODEL_DIR,
    "le_dict.pkl"
)

ISO_PATH = os.path.join(
    MODEL_DIR,
    "isolation_forest.pkl"
)

EMPLOYEE_PATH = os.path.join(
    MODEL_DIR,
    "employees.json"
)


# ============================================================
# LOAD MODEL
# ============================================================

print("=" * 60)
print("INSIGHTGUARD PRO")
print("=" * 60)

print("Base directory:")
print(BASE_DIR)

print("\nLoading model files...")


with open(
    MODEL_PATH,
    "rb"
) as f:

    model = pickle.load(f)


with open(
    SCALER_PATH,
    "rb"
) as f:

    scaler = pickle.load(f)


with open(
    FEATURE_PATH,
    "rb"
) as f:

    feature_columns = pickle.load(f)


# Label encoders

if os.path.exists(LE_PATH):

    with open(
        LE_PATH,
        "rb"
    ) as f:

        le_dict = pickle.load(f)

else:

    le_dict = {}


# Isolation Forest

if os.path.exists(ISO_PATH):

    with open(
        ISO_PATH,
        "rb"
    ) as f:

        isolation_forest = pickle.load(f)

else:

    isolation_forest = None


print("Model loaded")
print(
    "Features:",
    len(feature_columns)
)


# ============================================================
# LOAD EMPLOYEES
# ============================================================

employees = []


if os.path.exists(
    EMPLOYEE_PATH
):

    try:

        with open(
            EMPLOYEE_PATH,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)


        if isinstance(
            data,
            list
        ):

            employees = data

        elif isinstance(
            data,
            dict
        ):

            employees = data.get(
                "employees",
                []
            )


    except Exception as e:

        print(
            "employees.json error:",
            e
        )


print(
    "Employees:",
    len(employees)
)


# ============================================================
# SHAP
# ============================================================

try:

    explainer = shap.TreeExplainer(
        model
    )

    print("SHAP loaded")

except Exception as e:

    explainer = None

    print(
        "SHAP unavailable:",
        e
    )


# ============================================================
# FEATURE LABELS
# ============================================================

FEATURE_LABELS = {

    "logon_count":
        "Logon Count",

    "off_hours_logons":
        "Off-Hours Logons",

    "distinct_pcs":
        "Unique PCs",

    "usb_connects":
        "USB Connections",

    "off_hours_usb":
        "Off-Hours USB",

    "files_copied_to_usb":
        "Files Copied to USB",

    "sensitive_files_to_usb":
        "Sensitive Files to USB",

    "total_emails_sent":
        "Total Emails Sent",

    "external_emails_sent":
        "External Emails Sent",

    "total_attachments":
        "Total Attachments",

    "total_email_size":
        "Total Email Size",

    "http_count":
        "HTTP Requests",

    "unique_urls":
        "Unique URLs",

    "off_hours_http":
        "Off-Hours HTTP",

    "role_encoded":
        "Role",

    "department_encoded":
        "Department",

    "team_encoded":
        "Team",

    "supervisor_encoded":
        "Supervisor"
}


# ============================================================
# CREATE FIELD LIST
# ============================================================

fields = []


for feature in feature_columns:

    fields.append({

        "key":
            feature,

        "label":
            FEATURE_LABELS.get(
                feature,
                feature.replace(
                    "_",
                    " "
                ).title()
            )
    })


# ============================================================
# SEVERITY
# ============================================================

def get_severity(
    risk_score
):

    if risk_score >= 75:

        return (
            "Critical",
            "#f87171"
        )

    elif risk_score >= 50:

        return (
            "High",
            "#fb7185"
        )

    elif risk_score >= 25:

        return (
            "Medium",
            "#fbbf24"
        )

    else:

        return (
            "Low",
            "#4ade80"
        )


# ============================================================
# SHAP
# ============================================================

def calculate_shap(
    dataframe
):

    if explainer is None:

        return []


    try:

        values = explainer.shap_values(
            dataframe
        )


        if isinstance(
            values,
            list
        ):

            values = values[-1]


        values = values[0]


        factors = []


        for feature, value in zip(
            feature_columns,
            values
        ):

            factors.append({

                "feature":
                    FEATURE_LABELS.get(
                        feature,
                        feature
                    ),

                "shap_value":
                    round(
                        float(value),
                        4
                    )
            })


        factors.sort(
            key=lambda x:
                abs(
                    x["shap_value"]
                ),
            reverse=True
        )


        return factors[:8]


    except Exception as e:

        print(
            "SHAP error:",
            e
        )

        return []


# ============================================================
# PREDICTION
# ============================================================

def predict_behavior(
    payload
):

    values = {}


    for feature in feature_columns:

        value = payload.get(
            feature,
            0
        )


        try:

            value = float(
                value
            )

        except (
            ValueError,
            TypeError
        ):

            value = 0.0


        values[feature] = value


    dataframe = pd.DataFrame(
        [values],
        columns=feature_columns
    )


    # Scale exactly as training

    scaled = scaler.transform(
        dataframe
    )


    # Prediction

    prediction = int(
        model.predict(
            scaled
        )[0]
    )


    # Probability

    probability = float(
        model.predict_proba(
            scaled
        )[0][1]
    )


    risk_score = round(
        probability * 100,
        2
    )


    prediction_name = (
        "INSIDER"
        if prediction == 1
        else "NORMAL"
    )


    severity, severity_color = (
        get_severity(
            risk_score
        )
    )


    top_factors = calculate_shap(
        dataframe
    )


    return {

        "prediction":
            prediction_name,

        "severity":
            severity,

        "severity_color":
            severity_color,

        "risk_score_100":
            risk_score,

        "confidence":
            round(
                probability * 100,
                2
            ),

        "top_factors":
            top_factors
    }


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/")
def dashboard():

    total_employees = len(
        employees
    )


    stats = {

        "total_employees":
            total_employees,

        "total_predictions":
            0,

        "high_risk_count":
            0,

        "safe_count":
            total_employees
    }


    top_risk = []

    alerts = []


    return render_template(
        "dashboard.html",
        stats=stats,
        top_risk=top_risk,
        alerts=alerts
    )


# ============================================================
# EMPLOYEES
# ============================================================

@app.route(
    "/employees"
)
def employee_list():

    query = request.args.get(
        "q",
        ""
    ).strip()


    filtered = employees


    if query:

        q = query.lower()


        filtered = []


        for employee in employees:

            text = " ".join([

                str(
                    employee.get(
                        "user",
                        ""
                    )
                ),

                str(
                    employee.get(
                        "name",
                        ""
                    )
                ),

                str(
                    employee.get(
                        "department",
                        ""
                    )
                ),

                str(
                    employee.get(
                        "role",
                        ""
                    )
                )

            ]).lower()


            if q in text:

                filtered.append(
                    employee
                )


    result = []


    for employee in filtered:

        result.append({

            "user":
                employee.get(
                    "user",
                    ""
                ),

            "name":
                employee.get(
                    "name",
                    employee.get(
                        "user",
                        ""
                    )
                ),

            "department":
                employee.get(
                    "department",
                    "Unknown"
                ),

            "role":
                employee.get(
                    "role",
                    "Unknown"
                ),

            "status":
                employee.get(
                    "status",
                    "Safe"
                )
        })


    return render_template(

        "employees.html",

        employees=result,

        total=len(result),

        query=query
    )


# ============================================================
# PROFILE
# ============================================================

@app.route(
    "/employees/<user>"
)
def profile(user):

    employee = None


    for e in employees:

        if str(
            e.get(
                "user",
                ""
            )
        ) == str(user):

            employee = e

            break


    if employee is None:

        return (
            "Employee not found",
            404
        )


    emp = {

        "user":
            employee.get(
                "user",
                user
            ),

        "name":
            employee.get(
                "name",
                user
            ),

        "department":
            employee.get(
                "department",
                "Unknown"
            ),

        "role":
            employee.get(
                "role",
                "Unknown"
            ),

        "email":
            employee.get(
                "email",
                "N/A"
            ),

        "total_predictions":
            employee.get(
                "total_predictions",
                0
            ),

        "high_risk_days":
            employee.get(
                "high_risk_days",
                0
            ),

        "risk_score_100":
            employee.get(
                "risk_score_100",
                0
            ),

        "status":
            employee.get(
                "status",
                "Safe"
            )
    }


    return render_template(
        "profile.html",
        emp=emp
    )


# ============================================================
# PIPELINE
# ============================================================

@app.route(
    "/pipeline"
)
def pipeline():

    return render_template(
        "pipeline.html"
    )


# ============================================================
# PREDICTIONS
# ============================================================

@app.route(
    "/predictions"
)
def predictions():

    return render_template(
        "predictions.html",
        fields=fields
    )


# ============================================================
# PREDICT API
# ============================================================

@app.route(
    "/predict",
    methods=["POST"]
)
def predict_api():

    try:

        payload = request.get_json(
            silent=True
        )


        if payload is None:

            payload = {}


        result = predict_behavior(
            payload
        )


        return jsonify(
            result
        )


    except Exception as e:

        print(
            "Prediction error:",
            e
        )


        return jsonify({

            "error":
                str(e)

        }), 500


# ============================================================
# PDF REPORT
# ============================================================

@app.route(
    "/export/pdf",
    methods=["POST"]
)
def export_pdf():

    try:

        data = request.get_json(
            silent=True
        ) or {}


        buffer = io.BytesIO()


        pdf = canvas.Canvas(
            buffer,
            pagesize=letter
        )


        width, height = letter


        # Header

        pdf.setFont(
            "Helvetica-Bold",
            20
        )


        pdf.drawString(
            50,
            height - 50,
            "InsightGuard Pro"
        )


        pdf.setFont(
            "Helvetica",
            11
        )


        pdf.drawString(
            50,
            height - 70,
            "AI Insider Threat Behavioural Intelligence Report"
        )


        y = height - 120


        # Prediction

        pdf.setFont(
            "Helvetica-Bold",
            12
        )


        pdf.drawString(
            50,
            y,
            "Prediction:"
        )


        pdf.setFont(
            "Helvetica",
            12
        )


        pdf.drawString(
            150,
            y,
            str(
                data.get(
                    "prediction",
                    "N/A"
                )
            )
        )


        y -= 25


        # Severity

        pdf.setFont(
            "Helvetica-Bold",
            12
        )


        pdf.drawString(
            50,
            y,
            "Severity:"
        )


        pdf.setFont(
            "Helvetica",
            12
        )


        pdf.drawString(
            150,
            y,
            str(
                data.get(
                    "severity",
                    "N/A"
                )
            )
        )


        y -= 25


        # Score

        pdf.setFont(
            "Helvetica-Bold",
            12
        )


        pdf.drawString(
            50,
            y,
            "Risk Score:"
        )


        pdf.setFont(
            "Helvetica",
            12
        )


        pdf.drawString(
            150,
            y,
            str(
                data.get(
                    "risk_score_100",
                    "N/A"
                )
            )
            + "/100"
        )


        y -= 40


        # Factors

        pdf.setFont(
            "Helvetica-Bold",
            12
        )


        pdf.drawString(
            50,
            y,
            "Top SHAP Factors"
        )


        y -= 25


        pdf.setFont(
            "Helvetica",
            10
        )


        factors = data.get(
            "top_factors",
            []
        )


        for factor in factors:

            feature = factor.get(
                "feature",
                "Unknown"
            )


            value = factor.get(
                "shap_value",
                0
            )


            pdf.drawString(
                60,
                y,
                f"{feature}: {value}"
            )


            y -= 18


        y -= 20


        pdf.drawString(
            50,
            y,
            "Generated by InsightGuard Pro"
        )


        pdf.save()


        buffer.seek(0)


        return send_file(

            buffer,

            mimetype=
                "application/pdf",

            as_attachment=True,

            download_name=
                "investigation_report.pdf"
        )


    except Exception as e:

        return jsonify({

            "error":
                str(e)

        }), 500


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route(
    "/health"
)
def health():

    return jsonify({

        "status":
            "running",

        "model":
            "XGBoost",

        "features":
            len(feature_columns),

        "employees":
            len(employees)

    })


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print(
        "InsightGuard Pro starting..."
    )
    print("=" * 60)

    print(
        f"Local URL: http://127.0.0.1:{PORT}"
    )

    print(
        f"Template folder: {TEMPLATE_DIR}"
    )

    print(
        f"Templates exist: {os.path.exists(TEMPLATE_DIR)}"
    )

    print("=" * 60)


    app.run(

        host="0.0.0.0",

        port=PORT,

        debug=False
    )
