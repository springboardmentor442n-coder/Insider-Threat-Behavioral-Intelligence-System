import os
import io
import json
import pickle

import pandas as pd
import shap

from flask import Flask, request, jsonify, send_file, render_template
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_DIR = "model"

app = Flask(__name__)


# ============================================================
# LOAD MODEL FILES
# ============================================================

with open(os.path.join(MODEL_DIR, "model.pkl"), "rb") as f:
    model = pickle.load(f)

with open(os.path.join(MODEL_DIR, "scaler.pkl"), "rb") as f:
    scaler = pickle.load(f)

with open(os.path.join(MODEL_DIR, "feature_columns.pkl"), "rb") as f:
    FEATURE_COLS = pickle.load(f)

print("Model loaded.")
print("Features expected by model:")
print(FEATURE_COLS)


# ============================================================
# LOAD EMPLOYEE DATA
# ============================================================

EMPLOYEE_FILE = os.path.join(MODEL_DIR, "employees.json")

employees_data = []

if os.path.exists(EMPLOYEE_FILE):
    try:
        with open(EMPLOYEE_FILE, "r", encoding="utf-8") as f:
            employees_json = json.load(f)

        if isinstance(employees_json, dict):
            employees_data = employees_json.get("employees", [])
        elif isinstance(employees_json, list):
            employees_data = employees_json

        print(f"Loaded {len(employees_data)} employees.")

    except Exception as e:
        print("Could not load employees.json:", e)


# ============================================================
# SHAP
# ============================================================

try:
    explainer = shap.TreeExplainer(model)
    print("SHAP explainer ready.")
except Exception as e:
    explainer = None
    print("SHAP could not be initialized:", e)


# ============================================================
# FRONTEND INPUT FIELDS
# ============================================================

FIELD_LABELS = {
    "logon_count": "Logon Count",
    "off_hours_logons": "Off-Hours Logons",
    "distinct_pcs": "Unique PCs",
    "usb_connects": "USB Connects",
    "off_hours_usb": "Off-Hours USB",
    "files_copied_to_usb": "Files Copied to USB",
    "sensitive_files_to_usb": "Sensitive Files to USB",
    "total_emails_sent": "Emails Sent",
    "external_emails_sent": "External Emails",
    "total_attachments": "Attachments",
    "total_email_size": "Total Email Size",
    "role_encoded": "Role",
    "department_encoded": "Department",
    "team_encoded": "Team",
    "supervisor_encoded": "Supervisor",
}


MANUAL_FIELDS = [
    {
        "key": feature,
        "label": FIELD_LABELS.get(
            feature,
            feature.replace("_", " ").title()
        )
    }
    for feature in FEATURE_COLS
]


# ============================================================
# SEVERITY
# ============================================================

def severity_tier(score_100):

    if score_100 >= 80:
        return "Critical", "#f87171"

    if score_100 >= 60:
        return "High", "#fb923c"

    if score_100 >= 40:
        return "Medium", "#facc15"

    return "Low", "#4ade80"


# ============================================================
# SHAP FACTORS
# ============================================================

def get_shap_factors(input_df, top_n=5):

    if explainer is None:
        return []

    try:

        shap_values = explainer.shap_values(input_df)

        if isinstance(shap_values, list):
            vals = shap_values[-1][0]
        else:
            vals = shap_values[0]

        factor_pairs = list(zip(FEATURE_COLS, vals))

        factor_pairs.sort(
            key=lambda x: abs(float(x[1])),
            reverse=True
        )

        return [
            {
                "feature": feature,
                "shap_value": round(float(value), 4)
            }
            for feature, value in factor_pairs[:top_n]
        ]

    except Exception as e:

        print("SHAP error:", e)

        return []


# ============================================================
# RUN PREDICTION
# ============================================================

def run_prediction(row_vals):

    # Create dataframe using EXACT model features
    input_data = {}

    for feature in FEATURE_COLS:

        value = row_vals.get(feature, 0)

        try:
            value = float(value)
        except (ValueError, TypeError):
            value = 0.0

        input_data[feature] = value

    input_df = pd.DataFrame([input_data])

    # Ensure correct feature order
    input_df = input_df[FEATURE_COLS]

    # Scale
    scaled = scaler.transform(input_df)

    # Prediction
    pred = model.predict(scaled)[0]

    # Probability
    probability = float(
        model.predict_proba(scaled)[0][1]
    )

    # Score 0-100
    score_100 = round(probability * 100, 1)

    # Severity
    severity, color = severity_tier(score_100)

    # SHAP
    factors = get_shap_factors(input_df)

    return {
        "prediction": "INSIDER" if int(pred) == 1 else "Normal",
        "risk_score": round(probability, 4),
        "risk_score_100": score_100,
        "severity": severity,
        "severity_color": color,
        "top_factors": factors,
        "raw_input": row_vals
    }


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/")
def index():

    total_employees = len(employees_data)

    # These values can later be connected to stored predictions.
    stats = {
        "total_employees": total_employees,
        "total_predictions": 0,
        "high_risk_count": 0,
        "safe_count": 0
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
# EMPLOYEE LIST
# ============================================================

@app.route("/employees")
def employees_page():

    query = request.args.get("q", "").strip().lower()

    employee_list = employees_data

    if query:

        employee_list = [
            employee
            for employee in employees_data
            if query in str(employee.get("user", "")).lower()
            or query in str(employee.get("name", "")).lower()
            or query in str(employee.get("department", "")).lower()
            or query in str(employee.get("role", "")).lower()
        ]

    processed_employees = []

    for employee in employee_list:

        processed = {
            "user": employee.get("user", ""),
            "name": employee.get("name", employee.get("user", "")),
            "department": employee.get("department", "N/A"),
            "role": employee.get("role", "N/A"),
            "status": employee.get("status", "Safe")
        }

        processed_employees.append(processed)

    return render_template(
        "employees.html",
        employees=processed_employees,
        total=len(processed_employees),
        query=query
    )


# ============================================================
# EMPLOYEE PROFILE
# ============================================================

@app.route("/employees/<user>")
def employee_profile(user):

    employee = None

    for e in employees_data:

        if str(e.get("user", "")) == str(user):
            employee = e
            break

    if employee is None:
        return "Employee not found", 404

    # Provide defaults expected by profile.html

    emp = {
        "user": employee.get("user", user),
        "name": employee.get(
            "name",
            employee.get("user", user)
        ),
        "department": employee.get(
            "department",
            "N/A"
        ),
        "role": employee.get(
            "role",
            "N/A"
        ),
        "email": employee.get(
            "email",
            "N/A"
        ),
        "total_predictions": employee.get(
            "total_predictions",
            0
        ),
        "high_risk_days": employee.get(
            "high_risk_days",
            0
        ),
        "risk_score_100": employee.get(
            "risk_score_100",
            0
        ),
        "status": employee.get(
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

@app.route("/pipeline")
def pipeline():

    return render_template(
        "pipeline.html"
    )


# ============================================================
# PREDICTIONS PAGE
# ============================================================

@app.route("/predictions")
def predictions():

    return render_template(
        "predictions.html",
        fields=MANUAL_FIELDS
    )


# ============================================================
# PREDICTION API
# ============================================================

@app.route("/predict", methods=["POST"])
def predict():

    try:

        data = request.get_json(force=True) or {}

        result = run_prediction(data)

        return jsonify(result)

    except Exception as ex:

        print("Prediction error:", ex)

        return jsonify({
            "error": str(ex)
        }), 400


# ============================================================
# PDF EXPORT
# ============================================================

@app.route("/export/pdf", methods=["POST"])
def export_pdf():

    try:

        data = request.get_json(force=True) or {}

        buf = io.BytesIO()

        c = canvas.Canvas(
            buf,
            pagesize=letter
        )

        width, height = letter

        # Header
        c.setFillColorRGB(
            0.04,
            0.06,
            0.12
        )

        c.rect(
            0,
            height - 80,
            width,
            80,
            fill=1
        )

        c.setFillColorRGB(
            1,
            1,
            1
        )

        c.setFont(
            "Helvetica-Bold",
            18
        )

        c.drawString(
            50,
            height - 45,
            "InsightGuard — Investigation Report"
        )

        c.setFont(
            "Helvetica",
            10
        )

        c.drawString(
            50,
            height - 65,
            f"Generated: "
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

        # Prediction
        y = height - 120

        c.setFillColorRGB(
            0,
            0,
            0
        )

        c.setFont(
            "Helvetica-Bold",
            14
        )

        c.drawString(
            50,
            y,
            f"Prediction: "
            f"{data.get('prediction', 'N/A')}"
        )

        y -= 25

        c.drawString(
            50,
            y,
            f"Risk Score: "
            f"{data.get('risk_score_100', 'N/A')}/100 "
            f"({data.get('severity', 'N/A')} Severity)"
        )

        y -= 35

        # SHAP
        c.setFont(
            "Helvetica-Bold",
            12
        )

        c.drawString(
            50,
            y,
            "Top Contributing Factors (SHAP):"
        )

        y -= 20

        c.setFont(
            "Helvetica",
            10
        )

        for factor in data.get("top_factors", []):

            c.drawString(
                60,
                y,
                f"- {factor.get('feature', 'N/A')}: "
                f"{factor.get('shap_value', 'N/A')}"
            )

            y -= 16

        # Raw input
        y -= 20

        c.setFont(
            "Helvetica-Bold",
            12
        )

        c.drawString(
            50,
            y,
            "Raw Input Values:"
        )

        y -= 20

        c.setFont(
            "Helvetica",
            9
        )

        for key, value in data.get(
            "raw_input",
            {}
        ).items():

            c.drawString(
                60,
                y,
                f"{key}: {value}"
            )

            y -= 14

            if y < 60:

                c.showPage()

                y = height - 60

        c.save()

        buf.seek(0)

        return send_file(
            buf,
            mimetype="application/pdf",
            as_attachment=True,
            download_name="investigation_report.pdf"
        )

    except Exception as ex:

        print("PDF error:", ex)

        return jsonify({
            "error": str(ex)
        }), 400


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    port = int(
        os.getenv(
            "FLASK_PORT",
            5000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
