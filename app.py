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
    redirect,
    url_for,
    session
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

ENV_PATH = os.path.join(
    BASE_DIR,
    ".env"
)

EMPLOYEE_PATH = os.path.join(
    MODEL_DIR,
    "employees.json"
)

PREDICTION_PATH = os.path.join(
    BASE_DIR,
    "predictions.json"
)


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv(ENV_PATH)

PORT = int(
    os.getenv(
        "FLASK_PORT",
        "5000"
    )
)

ADMIN_EMAIL = os.getenv(
    "ADMIN_EMAIL",
    ""
).strip()

ADMIN_PASSWORD = os.getenv(
    "ADMIN_PASSWORD",
    ""
)

FLASK_SECRET_KEY = os.getenv(
    "FLASK_SECRET_KEY",
    "change-this-secret-key"
)


# ============================================================
# FLASK
# ============================================================

app = Flask(
    __name__,
    template_folder=TEMPLATE_DIR
)

app.secret_key = FLASK_SECRET_KEY


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
# STARTUP
# ============================================================

print("=" * 60)
print("INSIGHTGUARD PRO")
print("=" * 60)

print()
print("Base directory:")
print(BASE_DIR)

print()
print("Loading model files...")


# ============================================================
# LOAD MODEL
# ============================================================

try:

    with open(
        MODEL_PATH,
        "rb"
    ) as f:

        model = pickle.load(f)

except Exception as e:

    print(
        "MODEL LOAD ERROR:",
        e
    )

    model = None


# ============================================================
# LOAD SCALER
# ============================================================

try:

    with open(
        SCALER_PATH,
        "rb"
    ) as f:

        scaler = pickle.load(f)

except Exception as e:

    print(
        "SCALER LOAD ERROR:",
        e
    )

    scaler = None


# ============================================================
# LOAD FEATURES
# ============================================================

try:

    with open(
        FEATURE_PATH,
        "rb"
    ) as f:

        feature_columns = pickle.load(f)

except Exception as e:

    print(
        "FEATURE LOAD ERROR:",
        e
    )

    feature_columns = []


# ============================================================
# LOAD LABEL ENCODERS
# ============================================================

if os.path.exists(
    LE_PATH
):

    try:

        with open(
            LE_PATH,
            "rb"
        ) as f:

            le_dict = pickle.load(f)

    except Exception as e:

        print(
            "LABEL ENCODER ERROR:",
            e
        )

        le_dict = {}

else:

    le_dict = {}


# ============================================================
# LOAD ISOLATION FOREST
# ============================================================

if os.path.exists(
    ISO_PATH
):

    try:

        with open(
            ISO_PATH,
            "rb"
        ) as f:

            isolation_forest = pickle.load(f)

    except Exception as e:

        print(
            "ISOLATION FOREST ERROR:",
            e
        )

        isolation_forest = None

else:

    isolation_forest = None


print()
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
        PREDICTION_PATH
    ):

        return []

    try:

        with open(
            PREDICTION_PATH,
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
            "predictions.json error:",
            e
        )

        return []


def save_predictions(
    data
):

    try:

        with open(
            PREDICTION_PATH,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                data,
                f,
                indent=4
            )

        return True

    except Exception as e:

        print(
            "Prediction save error:",
            e
        )

        return False


predictions_history = load_predictions()


# ============================================================
# SHAP
# ============================================================

try:

    if model is not None:

        explainer = shap.TreeExplainer(
            model
        )

        print(
            "SHAP loaded"
        )

    else:

        explainer = None

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

            except (
                ValueError,
                TypeError
            ):

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
# PREDICTION FUNCTION
# ============================================================

def predict_behavior(
    payload
):

    if model is None:

        raise RuntimeError(
            "Model is not loaded."
        )

    if scaler is None:

        raise RuntimeError(
            "Scaler is not loaded."
        )

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
    try:

        probability = float(
            model.predict_proba(
                scaled
            )[0][1]
        )

    except Exception:

        probability = float(
            prediction
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
# LOGIN REQUIRED DECORATOR
# ============================================================

def login_required(
    function
):

    @wraps(function)
    def wrapper(
        *args,
        **kwargs
    ):

        if not session.get(
            "logged_in"
        ):

            return redirect(
                url_for(
                    "login"
                )
            )

        return function(
            *args,
            **kwargs
        )

    return wrapper


# ============================================================
# LOGIN
# ============================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if session.get(
        "logged_in"
    ):

        return redirect(
            url_for(
                "dashboard"
            )
        )

    error = None

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        if (
            email == ADMIN_EMAIL
            and
            password == ADMIN_PASSWORD
        ):

            session.clear()

            session["logged_in"] = True
            session["user_email"] = email

            return redirect(
                url_for(
                    "dashboard"
                )
            )

        error = (
            "Invalid email or password."
        )

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
        url_for(
            "login"
        )
    )


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/")
@login_required
def dashboard():

    history = load_predictions()

    total_employees = len(
        employees
    )

    total_predictions = len(
        history
    )

    high_risk_predictions = [
        p
        for p in history
        if p.get(
            "prediction"
        ) == "INSIDER"
    ]

    high_risk_count = len(
        high_risk_predictions
    )

    safe_count = (
        total_predictions
        -
        high_risk_count
    )

    if safe_count < 0:

        safe_count = 0

    stats = {

        "total_employees":
            total_employees,

        "total_predictions":
            total_predictions,

        "high_risk_count":
            high_risk_count,

        "safe_count":
            safe_count
    }

    # Latest high-risk predictions
    alerts = []

    for prediction in reversed(
        history
    ):

        if prediction.get(
            "prediction"
        ) == "INSIDER":

            alerts.append({

                "name":
                    prediction.get(
                        "employee",
                        "Unknown"
                    ),

                "day":
                    prediction.get(
                        "timestamp",
                        ""
                    )
            })

        if len(
            alerts
        ) >= 10:

            break

    # Top risk predictions
    sorted_history = sorted(
        history,
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

    for prediction in sorted_history[:10]:

        top_risk.append({

            "user":
                prediction.get(
                    "employee_id",
                    "N/A"
                ),

            "name":
                prediction.get(
                    "employee",
                    "Unknown"
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
                (
                    "High Risk"
                    if prediction.get(
                        "prediction"
                    ) == "INSIDER"
                    else "Safe"
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
                    ""
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
def profile(
    user
):

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

    # Calculate history for this employee
    employee_predictions = [

        p
        for p in load_predictions()

        if str(
            p.get(
                "employee_id",
                ""
            )
        ) == str(user)
    ]

    high_risk_days = len([

        p
        for p in employee_predictions

        if p.get(
            "prediction"
        ) == "INSIDER"

    ])

    latest_risk = 0

    if employee_predictions:

        latest_risk = employee_predictions[-1].get(
            "risk_score_100",
            0
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
                employee_predictions
            ),

        "high_risk_days":
            high_risk_days,

        "risk_score_100":
            latest_risk,

        "status":
            (
                "High Risk"
                if latest_risk >= 50
                else "Safe"
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

        # ----------------------------------------------------
        # Employee information from request
        # ----------------------------------------------------

        employee_id = payload.get(
            "employee_id",
            ""
        )

        employee_name = payload.get(
            "employee_name",
            ""
        )

        # Try to find employee
        if employee_id and not employee_name:

            for employee in employees:

                if str(
                    employee.get(
                        "user",
                        ""
                    )
                ) == str(
                    employee_id
                ):

                    employee_name = employee.get(
                        "name",
                        employee_id
                    )

                    break

        if not employee_name:

            employee_name = (
                "Manual Prediction"
            )

        # ----------------------------------------------------
        # Save prediction
        # ----------------------------------------------------

        record = {

            "id":
                len(
                    predictions_history
                ) + 1,

            "employee_id":
                employee_id,

            "employee":
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
                ),

            "timestamp":
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),

            "created_by":
                session.get(
                    "user_email",
                    ""
                )
        }

        predictions_history.append(
            record
        )

        save_predictions(
            predictions_history
        )

        # ----------------------------------------------------
        # Update employee
        # ----------------------------------------------------

        if employee_id:

            for employee in employees:

                if str(
                    employee.get(
                        "user",
                        ""
                    )
                ) == str(
                    employee_id
                ):

                    employee[
                        "total_predictions"
                    ] = employee.get(
                        "total_predictions",
                        0
                    ) + 1

                    if result.get(
                        "prediction"
                    ) == "INSIDER":

                        employee[
                            "high_risk_days"
                        ] = employee.get(
                            "high_risk_days",
                            0
                        ) + 1

                    employee[
                        "risk_score_100"
                    ] = result.get(
                        "risk_score_100",
                        0
                    )

                    employee[
                        "status"
                    ] = (

                        "High Risk"

                        if result.get(
                            "prediction"
                        ) == "INSIDER"

                        else "Safe"
                    )

                    break

            try:

                with open(
                    EMPLOYEE_PATH,
                    "w",
                    encoding="utf-8"
                ) as f:

                    json.dump(
                        employees,
                        f,
                        indent=4
                    )

            except Exception as e:

                print(
                    "Employee save error:",
                    e
                )

        # Return result to frontend
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

        # ----------------------------------------------------
        # Header
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # Prediction
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # Severity
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # Risk Score
        # ----------------------------------------------------

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
                    0
                )
            )
            + "/100"
        )

        y -= 25

        # ----------------------------------------------------
        # Confidence
        # ----------------------------------------------------

        pdf.setFont(
            "Helvetica-Bold",
            12
        )

        pdf.drawString(
            50,
            y,
            "Confidence:"
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
                    "confidence",
                    0
                )
            )
            + "%"
        )

        y -= 40

        # ----------------------------------------------------
        # SHAP FACTORS
        # ----------------------------------------------------

        pdf.setFont(
            "Helvetica-Bold",
            14
        )

        pdf.drawString(
            50,
            y,
            "Top Risk Factors"
        )

        y -= 25

        factors = data.get(
            "top_factors",
            []
        )

        pdf.setFont(
            "Helvetica",
            10
        )

        for factor in factors:

            feature = str(
                factor.get(
                    "feature",
                    ""
                )
            )

            value = str(
                factor.get(
                    "shap_value",
                    ""
                )
            )

            pdf.drawString(
                60,
                y,
                feature + ": " + value
            )

            y -= 18

            if y < 60:

                pdf.showPage()

                y = height - 60

                pdf.setFont(
                    "Helvetica",
                    10
                )

        # ----------------------------------------------------
        # Footer
        # ----------------------------------------------------

        pdf.setFont(
            "Helvetica",
            8
        )

        pdf.drawString(
            50,
            30,
            "Generated by InsightGuard Pro"
        )

        pdf.save()

        buffer.seek(0)

        return send_file(
            buffer,
            as_attachment=True,
            download_name="investigation_report.pdf",
            mimetype="application/pdf"
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
            "ok",

        "model_loaded":
            model is not None,

        "features":
            len(feature_columns),

        "employees":
            len(employees),

        "predictions":
            len(
                load_predictions()
            )
    })


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    print()
    print(
        "Starting InsightGuard..."
    )

    print(
        "Login:",
        "http://127.0.0.1:" + str(PORT) + "/login"
    )

    print(
        "Dashboard:",
        "http://127.0.0.1:" + str(PORT) + "/"
    )

    print()

    app.run(
        host="0.0.0.0",
        port=PORT,
        debug=False
    )
