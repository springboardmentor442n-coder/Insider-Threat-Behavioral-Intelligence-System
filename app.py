import os
import io
import json
import pickle
from datetime import datetime
from functools import wraps

import pandas as pd
import shap

from flask import (
    Flask,
    request,
    jsonify,
    render_template,
    send_file,
    session,
    redirect,
    url_for
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

EMPLOYEE_PATH = os.path.join(
    MODEL_DIR,
    "employees.json"
)

PREDICTIONS_PATH = os.path.join(
    BASE_DIR,
    "predictions.json"
)


# ============================================================
# ENVIRONMENT
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

ADMIN_EMAIL = os.getenv(
    "ADMIN_EMAIL",
    "admin@example.com"
)

ADMIN_PASSWORD = os.getenv(
    "ADMIN_PASSWORD",
    "admin123"
)

SECRET_KEY = os.getenv(
    "FLASK_SECRET_KEY",
    "insightguard-secret-key-change-this"
)


# ============================================================
# FLASK
# ============================================================

app = Flask(
    __name__,
    template_folder=TEMPLATE_DIR
)

app.secret_key = SECRET_KEY


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


if os.path.exists(LE_PATH):

    with open(
        LE_PATH,
        "rb"
    ) as f:
        le_dict = pickle.load(f)

else:

    le_dict = {}


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
# PREDICTION STORAGE
# ============================================================

def load_predictions():

    if not os.path.exists(
        PREDICTIONS_PATH
    ):
        return []

    try:

        with open(
            PREDICTIONS_PATH,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

        if isinstance(
            data,
            list
        ):
            return data

        return []

    except Exception as e:

        print(
            "Prediction history error:",
            e
        )

        return []


def save_prediction(record):

    predictions = load_predictions()

    predictions.append(
        record
    )

    with open(
        PREDICTIONS_PATH,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            predictions,
            f,
            indent=2
        )


# ============================================================
# LOGIN PROTECTION
# ============================================================

def login_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        if not session.get(
            "logged_in"
        ):

            return redirect(
                url_for("login")
            )

        return function(
            *args,
            **kwargs
        )

    return wrapper


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
# SHAP CALCULATION
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

            try:

                numeric_value = float(
                    value
                )

            except Exception:

                continue

            factors.append({

                "feature":
                    FEATURE_LABELS.get(
                        feature,
                        feature
                    ),

                "shap_value":
                    round(
                        numeric_value,
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

        else

        "NORMAL"
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
# LOGIN
# ============================================================

@app.route(
    "/login",
    methods=[
        "GET",
        "POST"
    ]
)
def login():

    if session.get(
        "logged_in"
    ):

        return redirect(
            url_for("dashboard")
        )


    error = None


    if request.method == "POST":

        email = (
            request.form
            .get(
                "email",
                ""
            )
            .strip()
            .lower()
        )

        password = request.form.get(
            "password",
            ""
        )


        if (
            email == ADMIN_EMAIL.lower()
            and
            password == ADMIN_PASSWORD
        ):

            session.clear()

            session["logged_in"] = True

            session["email"] = email

            return redirect(
                url_for("dashboard")
            )


        error = "Invalid email or password."


    return render_template(
        "login.html",
        error=error
    )


# ============================================================
# LOGOUT
# ============================================================

@app.route(
    "/logout"
)
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/")
@login_required
def dashboard():

    prediction_history = (
        load_predictions()
    )


    total_employees = len(
        employees
    )


    total_predictions = len(
        prediction_history
    )


    high_risk_predictions = [

        p

        for p in prediction_history

        if p.get(
            "prediction"
        ) == "INSIDER"
    ]


    safe_predictions = [

        p

        for p in prediction_history

        if p.get(
            "prediction"
        ) == "NORMAL"
    ]


    stats = {

        "total_employees":
            total_employees,

        "total_predictions":
            total_predictions,

        "high_risk_count":
            len(
                high_risk_predictions
            ),

        "safe_count":
            len(
                safe_predictions
            )
    }


    sorted_predictions = sorted(

        prediction_history,

        key=lambda x:
            float(
                x.get(
                    "risk_score_100",
                    0
                )
            ),

        reverse=True
    )


    top_risk = []


    for prediction in sorted_predictions[:10]:

        top_risk.append({

            "user":
                prediction.get(
                    "employee_id",
                    "Manual Analysis"
                ),

            "name":
                prediction.get(
                    "employee_name",
                    prediction.get(
                        "employee_id",
                        "Manual Analysis"
                    )
                ),

            "risk_score_100":
                prediction.get(
                    "risk_score_100",
                    0
                ),

            "confidence":
                prediction.get(
                    "confidence",
                    0
                ),

            "status":
                "High Risk"

                if prediction.get(
                    "prediction"
                ) == "INSIDER"

                else

                "Safe"
        })


    alerts = []

    for prediction in sorted_predictions[:10]:

        if prediction.get(
            "prediction"
        ) == "INSIDER":

            alerts.append({

                "name":
                    prediction.get(
                        "employee_name",
                        prediction.get(
                            "employee_id",
                            "Unknown"
                        )
                    ),

                "day":
                    prediction.get(
                        "timestamp",
                        ""
                    )
            })


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
@login_required
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
@login_required
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


    # Calculate prediction information
    history = load_predictions()

    user_predictions = [

        p

        for p in history

        if str(
            p.get(
                "employee_id",
                ""
            )
        ) == str(user)
    ]


    high_risk_days = sum(

        1

        for p in user_predictions

        if p.get(
            "prediction"
        ) == "INSIDER"
    )


    if user_predictions:

        latest = max(

            user_predictions,

            key=lambda x:
                x.get(
                    "timestamp",
                    ""
                )
        )

        risk_score = latest.get(
            "risk_score_100",
            0
        )

        status = (

            "High Risk"

            if latest.get(
                "prediction"
            ) == "INSIDER"

            else

            "Safe"
        )

    else:

        risk_score = employee.get(
            "risk_score_100",
            0
        )

        status = employee.get(
            "status",
            "Safe"
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
            len(
                user_predictions
            ),

        "high_risk_days":
            high_risk_days,

        "risk_score_100":
            risk_score,

        "status":
            status
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
@login_required
def pipeline():

    return render_template(
        "pipeline.html"
    )


# ============================================================
# PREDICTIONS PAGE
# ============================================================

@app.route(
    "/predictions"
)
@login_required
def predictions():

    history = load_predictions()

    history.reverse()


    return render_template(
        "predictions.html",
        fields=fields,
        prediction_history=history
    )


# ============================================================
# PREDICT API
# ============================================================

@app.route(
    "/predict",
    methods=["POST"]
)
@login_required
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


        # ====================================================
        # SAVE PREDICTION
        # ====================================================

        employee_id = payload.get(
            "employee_id",
            "Manual Analysis"
        )

        employee_name = payload.get(
            "employee_name",
            "Manual Analysis"
        )


        record = {

            "timestamp":
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),

            "user_email":
                session.get(
                    "email",
                    "unknown"
                ),

            "employee_id":
                employee_id,

            "employee_name":
                employee_name,

            "prediction":
                result.get(
                    "prediction"
                ),

            "severity":
                result.get(
                    "severity"
                ),

            "risk_score_100":
                result.get(
                    "risk_score_100"
                ),

            "confidence":
                result.get(
                    "confidence"
                ),

            "top_factors":
                result.get(
                    "top_factors",
                    []
                )
        }


        save_prediction(
            record
        )


        # Add saved information to response

        result["timestamp"] = record[
            "timestamp"
        ]

        result["employee_id"] = (
            employee_id
        )

        result["employee_name"] = (
            employee_name
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
# PREDICTION HISTORY API
# ============================================================

@app.route(
    "/api/predictions"
)
@login_required
def prediction_history_api():

    history = load_predictions()

    history.reverse()

    return jsonify(
        history
    )


# ============================================================
# PDF REPORT
# ============================================================

@app.route(
    "/export/pdf",
    methods=["POST"]
)
@login_required
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


        # Employee

        pdf.setFont(
            "Helvetica-Bold",
            12
        )

        pdf.drawString(
            50,
            y,
            "Employee:"
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
                    "employee_name",
                    "Manual Analysis"
                )
            )
        )


        y -= 25


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


        # Risk

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
            ) + "/100"
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

            mimetype="application/pdf",

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
            len(
                feature_columns
            ),

        "employees":
            len(
                employees
            ),

        "predictions":
            len(
                load_predictions()
            )
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

    print(
        f"Login email: {ADMIN_EMAIL}"
    )

    print(
        f"Prediction history: {PREDICTIONS_PATH}"
    )

    print("=" * 60)


    app.run(
        host="0.0.0.0",
        port=PORT,
        debug=False
    )
