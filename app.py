import os
import io
import json
import pickle
from datetime import datetime
from functools import wraps

import pandas as pd
import shap

from openai import OpenAI

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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "model")
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
EMPLOYEE_PATH = os.path.join(MODEL_DIR, "employees.json")
PREDICTION_HISTORY_PATH = os.path.join(BASE_DIR, "prediction_history.json")


# ============================================================
# ENV
# ============================================================

load_dotenv(os.path.join(BASE_DIR, ".env"))

PORT = int(os.getenv("FLASK_PORT", "5000"))
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "").strip()
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")


# ============================================================
# OPENAI
# ============================================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()

if OPENAI_API_KEY:
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
    print("OpenAI API configured")
else:
    openai_client = None
    print("OpenAI API key not configured")


# ============================================================
# FLASK
# ============================================================

app = Flask(__name__, template_folder=TEMPLATE_DIR)
app.secret_key = FLASK_SECRET_KEY


# ============================================================
# MODEL FILES
# ============================================================

MODEL_PATH = os.path.join(MODEL_DIR, "model.pkl")
SCALER_PATH = os.path.join(MODEL_DIR, "scaler.pkl")
FEATURE_PATH = os.path.join(MODEL_DIR, "feature_columns.pkl")
LE_PATH = os.path.join(MODEL_DIR, "le_dict.pkl")
ISO_PATH = os.path.join(MODEL_DIR, "isolation_forest.pkl")


# ============================================================
# START MESSAGE
# ============================================================

print("=" * 60)
print("INSIGHTGUARD PRO")
print("=" * 60)
print("Base directory:")
print(BASE_DIR)
print()
print("Loading model files...")


# ============================================================
# LOAD MODEL
# ============================================================

with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)

with open(SCALER_PATH, "rb") as f:
    scaler = pickle.load(f)

with open(FEATURE_PATH, "rb") as f:
    feature_columns = pickle.load(f)


# ============================================================
# LABEL ENCODERS
# ============================================================

if os.path.exists(LE_PATH):
    with open(LE_PATH, "rb") as f:
        le_dict = pickle.load(f)
else:
    le_dict = {}


# ============================================================
# ISOLATION FOREST
# ============================================================

if os.path.exists(ISO_PATH):
    with open(ISO_PATH, "rb") as f:
        isolation_forest = pickle.load(f)
else:
    isolation_forest = None

print("Model loaded")
print("Features:", len(feature_columns))


# ============================================================
# LOAD EMPLOYEES
# ============================================================

employees = []

if os.path.exists(EMPLOYEE_PATH):
    try:
        with open(EMPLOYEE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list):
            employees = data
        elif isinstance(data, dict):
            employees = data.get("employees", [])

    except Exception as e:
        print("employees.json error:", e)

print("Employees:", len(employees))


# ============================================================
# PREDICTION HISTORY
# ============================================================

def load_prediction_history():
    if not os.path.exists(PREDICTION_HISTORY_PATH):
        return []
    try:
        with open(PREDICTION_HISTORY_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
    except Exception as e:
        print("Prediction history error:", e)
    return []


def save_prediction_history(history):
    try:
        with open(PREDICTION_HISTORY_PATH, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=4)
        return True
    except Exception as e:
        print("Could not save prediction history:", e)
        return False


prediction_history = load_prediction_history()


# ============================================================
# SHAP
# ============================================================

try:
    explainer = shap.TreeExplainer(model)
    print("SHAP loaded")
except Exception as e:
    explainer = None
    print("SHAP unavailable:", e)


# ============================================================
# FEATURE LABELS
# ============================================================

FEATURE_LABELS = {
    "logon_count": "Logon Count",
    "off_hours_logons": "Off-Hours Logons",
    "distinct_pcs": "Unique PCs",
    "usb_connects": "USB Connections",
    "off_hours_usb": "Off-Hours USB",
    "files_copied_to_usb": "Files Copied to USB",
    "sensitive_files_to_usb": "Sensitive Files to USB",
    "total_emails_sent": "Total Emails Sent",
    "external_emails_sent": "External Emails Sent",
    "total_attachments": "Total Attachments",
    "total_email_size": "Total Email Size",
    "http_count": "HTTP Requests",
    "unique_urls": "Unique URLs",
    "off_hours_http": "Off-Hours HTTP",
    "role_encoded": "Role",
    "department_encoded": "Department",
    "team_encoded": "Team",
    "supervisor_encoded": "Supervisor"
}


# ============================================================
# CREATE FIELD LIST
# ============================================================

fields = []

for feature in feature_columns:
    fields.append({
        "key": feature,
        "label": FEATURE_LABELS.get(
            feature,
            feature.replace("_", " ").title()
        )
    })


# ============================================================
# AUTHENTICATION
# ============================================================

def login_required(function):
    @wraps(function)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return function(*args, **kwargs)
    return decorated_function


# ============================================================
# LOGIN
# ============================================================

@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("logged_in"):
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            session["logged_in"] = True
            session["user_email"] = email
            return redirect(url_for("dashboard"))

        return render_template("login.html", error="Invalid email or password")

    return render_template("login.html")


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ============================================================
# SEVERITY
# ============================================================

def get_severity(risk_score):
    if risk_score >= 75:
        return ("Critical", "#f87171")
    elif risk_score >= 50:
        return ("High", "#fb7185")
    elif risk_score >= 25:
        return ("Medium", "#fbbf24")
    else:
        return ("Low", "#4ade80")


# ============================================================
# SHAP
# ============================================================

def calculate_shap(dataframe):
    if explainer is None:
        return []

    try:
        values = explainer.shap_values(dataframe)

        if isinstance(values, list):
            values = values[-1]

        values = values[0]

        factors = []

        for feature, value in zip(feature_columns, values):
            try:
                shap_value = float(value)
            except Exception:
                continue

            factors.append({
                "feature": FEATURE_LABELS.get(feature, feature),
                "shap_value": round(shap_value, 4)
            })

        factors.sort(key=lambda x: abs(x["shap_value"]), reverse=True)

        return factors[:8]

    except Exception as e:
        print("SHAP error:", e)
        return []


# ============================================================
# PREDICTION
# ============================================================

def predict_behavior(payload):
    values = {}

    for feature in feature_columns:
        value = payload.get(feature, 0)
        try:
            value = float(value)
        except (ValueError, TypeError):
            value = 0.0
        values[feature] = value

    dataframe = pd.DataFrame([values], columns=feature_columns)

    scaled = scaler.transform(dataframe)

    prediction = int(model.predict(scaled)[0])
    probability = float(model.predict_proba(scaled)[0][1])
    risk_score = round(probability * 100, 2)

    prediction_name = "INSIDER" if prediction == 1 else "NORMAL"

    severity, severity_color = get_severity(risk_score)

    top_factors = calculate_shap(dataframe)

    return {
        "prediction": prediction_name,
        "severity": severity,
        "severity_color": severity_color,
        "risk_score_100": risk_score,
        "confidence": round(probability * 100, 2),
        "top_factors": top_factors
    }


# ============================================================
# SAVE PREDICTION
# ============================================================

def record_prediction(result, payload):
    global prediction_history

    record = {
        "id": len(prediction_history) + 1,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user_email": session.get("user_email", "unknown"),
        "prediction": result.get("prediction", "N/A"),
        "severity": result.get("severity", "N/A"),
        "risk_score_100": result.get("risk_score_100", 0),
        "confidence": result.get("confidence", 0),
        "top_factors": result.get("top_factors", []),
        "features": payload
    }

    prediction_history.append(record)
    save_prediction_history(prediction_history)

    return record


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/")
@login_required
def dashboard():
    total_employees = len(employees)
    total_predictions = len(prediction_history)

    high_risk_count = sum(
        1 for p in prediction_history
        if p.get("severity") in ["High", "Critical"]
    )

    safe_count = max(total_predictions - high_risk_count, 0)

    stats = {
        "total_employees": total_employees,
        "total_predictions": total_predictions,
        "high_risk_count": high_risk_count,
        "safe_count": safe_count
    }

    top_risk = sorted(
        prediction_history,
        key=lambda x: float(x.get("risk_score_100", 0)),
        reverse=True
    )[:10]

    alerts = [
        p for p in prediction_history
        if p.get("prediction") == "INSIDER"
    ][-10:]

    return render_template(
        "dashboard.html",
        stats=stats,
        top_risk=top_risk,
        alerts=alerts,
        prediction_history=prediction_history,
        user_email=session.get("user_email"),
        active="dashboard"
    )


# ============================================================
# EMPLOYEES
# ============================================================

@app.route("/employees")
@login_required
def employee_list():
    query = request.args.get("q", "").strip()

    filtered = employees

    if query:
        q = query.lower()
        filtered = []

        for employee in employees:
            text = " ".join([
                str(employee.get("user", "")),
                str(employee.get("name", "")),
                str(employee.get("department", "")),
                str(employee.get("role", ""))
            ]).lower()

            if q in text:
                filtered.append(employee)

    result = []

    for employee in filtered:
        result.append({
            "user": employee.get("user", ""),
            "name": employee.get("name", employee.get("user", "")),
            "department": employee.get("department", "Unknown"),
            "role": employee.get("role", "Unknown"),
            "status": employee.get("status", "Safe")
        })

    return render_template(
        "employees.html",
        employees=result,
        total=len(result),
        query=query,
        active="employees"
    )


# ============================================================
# PROFILE
# ============================================================

@app.route("/employees/<user>")
@login_required
def profile(user):
    employee = None

    for e in employees:
        if str(e.get("user", "")) == str(user):
            employee = e
            break

    if employee is None:
        return ("Employee not found", 404)

    emp = {
        "user": employee.get("user", user),
        "name": employee.get("name", user),
        "department": employee.get("department", "Unknown"),
        "role": employee.get("role", "Unknown"),
        "email": employee.get("email", "N/A"),
        "total_predictions": employee.get("total_predictions", 0),
        "high_risk_days": employee.get("high_risk_days", 0),
        "risk_score_100": employee.get("risk_score_100", 0),
        "status": employee.get("status", "Safe")
    }

    return render_template("profile.html", emp=emp, active="employees")


# ============================================================
# PIPELINE
# ============================================================

@app.route("/pipeline")
@login_required
def pipeline():
    return render_template("pipeline.html", active="pipeline")


# ============================================================
# PREDICTIONS PAGE
# ============================================================

@app.route("/predictions")
@login_required
def predictions():
    return render_template(
        "predictions.html",
        fields=fields,
        prediction_history=prediction_history,
        active="predictions"
    )


# ============================================================
# PREDICT API
# ============================================================

@app.route("/predict", methods=["POST"])
@login_required
def predict_api():
    try:
        payload = request.get_json(silent=True)

        if payload is None:
            payload = {}

        result = predict_behavior(payload)

        record_prediction(result, payload)

        return jsonify(result)

    except Exception as e:
        print("Prediction error:", e)
        return jsonify({"error": str(e)}), 500


# ============================================================
# PREDICTION HISTORY API
# ============================================================

@app.route("/prediction-history")
@login_required
def prediction_history_api():
    return jsonify(prediction_history)


# ============================================================
# CLEAR PREDICTION HISTORY
# ============================================================

@app.route("/prediction-history/clear", methods=["POST"])
@login_required
def clear_prediction_history():
    global prediction_history
    prediction_history = []
    save_prediction_history(prediction_history)
    return jsonify({"success": True})


# ============================================================
# PDF REPORT
# ============================================================

@app.route("/export/pdf", methods=["POST"])
@login_required
def export_pdf():
    try:
        data = request.get_json(silent=True) or {}

        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        pdf.setFont("Helvetica-Bold", 20)
        pdf.drawString(50, height - 50, "InsightGuard Pro")

        pdf.setFont("Helvetica", 11)
        pdf.drawString(50, height - 70, "AI Insider Threat Behavioural Intelligence Report")

        y = height - 120

        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(50, y, "Prediction:")
        pdf.setFont("Helvetica", 12)
        pdf.drawString(150, y, str(data.get("prediction", "N/A")))
        y -= 25

        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(50, y, "Severity:")
        pdf.setFont("Helvetica", 12)
        pdf.drawString(150, y, str(data.get("severity", "N/A")))
        y -= 25

        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(50, y, "Risk Score:")
        pdf.setFont("Helvetica", 12)
        pdf.drawString(150, y, str(data.get("risk_score_100", "N/A")) + "/100")
        y -= 40

        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(50, y, "Top SHAP Factors")
        y -= 25

        pdf.setFont("Helvetica", 10)

        factors = data.get("top_factors", [])

        for factor in factors:
            feature = factor.get("feature", "Unknown")
            value = factor.get("shap_value", 0)
            pdf.drawString(60, y, f"{feature}: {value}")
            y -= 18

        y -= 20
        pdf.drawString(50, y, "Generated by InsightGuard Pro")

        pdf.save()
        buffer.seek(0)

        return send_file(
            buffer,
            mimetype="application/pdf",
            as_attachment=True,
            download_name="investigation_report.pdf"
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/health")
def health():
    return jsonify({
        "status": "running",
        "model": "XGBoost",
        "features": len(feature_columns),
        "employees": len(employees),
        "predictions": len(prediction_history)
    })


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("InsightGuard Pro starting...")
    print("=" * 60)
    print(f"Local URL: http://127.0.0.1:{PORT}")
    print(f"Template folder: {TEMPLATE_DIR}")
    print(f"Templates exist: {os.path.exists(TEMPLATE_DIR)}")
    print(f"Login email configured: {bool(ADMIN_EMAIL)}")
    print(f"Prediction history: {len(prediction_history)}")
    print("=" * 60)

    ngrok_token = os.getenv("NGROK_AUTH_TOKEN")
    if ngrok_token:
        from pyngrok import ngrok, conf
        conf.get_default().auth_token = ngrok_token
        ngrok.kill()
        tunnel = ngrok.connect(f"127.0.0.1:{PORT}")
        print(f"🌐 Public URL: {tunnel.public_url}")

    app.run(
        host="0.0.0.0",
        port=PORT,
        debug=False
    )
