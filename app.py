import os
import io
import json
import pickle
import logging

import pandas as pd
import shap

from flask import Flask, request, jsonify, send_file, render_template
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


# ============================================================
# CONFIGURATION
# ============================================================

# Get absolute path to model directory (works from any working directory)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(SCRIPT_DIR, "model")

app = Flask(__name__, template_folder=os.path.join(SCRIPT_DIR, "templates"))


# ============================================================
# LOAD MODEL FILES
# ============================================================

model = None
scaler = None
FEATURE_COLS = []

try:
    model_path = os.path.join(MODEL_DIR, "model.pkl")
    scaler_path = os.path.join(MODEL_DIR, "scaler.pkl")
    features_path = os.path.join(MODEL_DIR, "feature_columns.pkl")
    
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found: {model_path}")
    if not os.path.exists(scaler_path):
        raise FileNotFoundError(f"Scaler file not found: {scaler_path}")
    if not os.path.exists(features_path):
        raise FileNotFoundError(f"Features file not found: {features_path}")
    
    with open(model_path, "rb") as f:
        model = pickle.load(f)
    
    with open(scaler_path, "rb") as f:
        scaler = pickle.load(f)
    
    with open(features_path, "rb") as f:
        FEATURE_COLS = pickle.load(f)
    
    logger.info("Model loaded successfully.")
    logger.info(f"Features expected by model: {FEATURE_COLS}")
    
except FileNotFoundError as e:
    logger.error(f"Model file error: {e}")
except Exception as e:
    logger.error(f"Failed to load model files: {e}")


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

        logger.info(f"Loaded {len(employees_data)} employees.")

    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error in employees.json: {e}")
    except Exception as e:
        logger.error(f"Could not load employees.json: {e}")
else:
    logger.warning(f"Employee file not found at: {EMPLOYEE_FILE}")


# ============================================================
# SHAP
# ============================================================

explainer = None
try:
    if model is not None:
        explainer = shap.TreeExplainer(model)
        logger.info("SHAP explainer initialized successfully.")
    else:
        logger.warning("Model not loaded; SHAP explainer cannot be initialized.")
except Exception as e:
    logger.warning(f"SHAP explainer could not be initialized: {e}")


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
        logger.error(f"SHAP error: {e}")
        return []


# ============================================================
# RUN PREDICTION
# ============================================================

def run_prediction(row_vals):
    """Run prediction on input data with validation."""
    
    # Validate model is loaded
    if model is None or scaler is None:
        logger.error("Model or scaler not loaded")
        raise ValueError("Model or scaler not available for predictions")
    
    if not row_vals or not isinstance(row_vals, dict):
        logger.error("Invalid input data")
        raise ValueError("Input data must be a non-empty dictionary")
    
    try:
        # Create dataframe using EXACT model features
        input_data = {}
        
        for feature in FEATURE_COLS:
            value = row_vals.get(feature, 0)
            
            try:
                value = float(value)
                # Validate reasonable ranges (avoid NaN/inf)
                if pd.isna(value) or pd.isinf(value):
                    logger.warning(f"Invalid value for {feature}: {value}, using 0")
                    value = 0.0
            except (ValueError, TypeError):
                logger.debug(f"Could not convert {feature}={value} to float, using 0")
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
        probability = float(model.predict_proba(scaled)[0][1])
        
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
    
    except Exception as e:
        logger.error(f"Prediction error: {e}", exc_info=True)
        raise


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

    except ValueError as ve:
        logger.warning(f"Prediction validation error: {ve}")
        return jsonify({"error": str(ve)}), 400
    except Exception as ex:
        logger.error(f"Prediction error: {ex}", exc_info=True)
        return jsonify({"error": str(ex)}), 500


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
            download_name="investigation_report.pdf",
            cache_timeout=0
        )

    except Exception as ex:
        logger.error(f"PDF generation error: {ex}", exc_info=True)
        return jsonify({"error": str(ex)}), 500


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":
    logger.info("Starting Insider Threat Detection application...")
    logger.info(f"Model DIR: {MODEL_DIR}")
    logger.info(f"Flask app running on http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)