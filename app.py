import pickle, io
import pandas as pd
import shap
from flask import Flask, request, jsonify, send_file, render_template
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

MODEL_DIR = "model"

with open(f"{MODEL_DIR}/model.pkl", "rb") as f:
    model = pickle.load(f)
with open(f"{MODEL_DIR}/scaler.pkl", "rb") as f:
    scaler = pickle.load(f)
with open(f"{MODEL_DIR}/feature_columns.pkl", "rb") as f:
    FEATURE_COLS = pickle.load(f)

explainer = shap.TreeExplainer(model)
print("SHAP explainer ready.")

app = Flask(__name__)

MANUAL_FIELDS = [
    {"key": "logon_count", "label": "Logon Count"},
    {"key": "off_hours_logons", "label": "Off-Hours Logons"},
    {"key": "distinct_pcs", "label": "Unique PCs"},
    {"key": "usb_connects", "label": "USB Connects"},
    {"key": "off_hours_usb", "label": "Off-Hours USB"},
    {"key": "files_copied_to_usb", "label": "Files Copied"},
    {"key": "sensitive_files_to_usb", "label": "Sensitive Files"},
    {"key": "total_emails_sent", "label": "Emails Sent"},
    {"key": "external_emails_sent", "label": "External Emails"},
    {"key": "total_attachments", "label": "Attachments"},
    {"key": "total_email_size", "label": "Email Size"},
    {"key": "http_requests", "label": "HTTP Requests"},
    {"key": "cloud_job_visits", "label": "Cloud/Job Visits"},
]

def severity_tier(score_100):
    if score_100 >= 80: return "Critical", "#f87171"
    if score_100 >= 60: return "High", "#fb923c"
    if score_100 >= 40: return "Medium", "#facc15"
    return "Low", "#4ade80"

def get_shap_factors(input_df, top_n=5):
    shap_values = explainer.shap_values(input_df)
    vals = shap_values[0] if isinstance(shap_values, list) else shap_values[0]
    factor_pairs = list(zip(FEATURE_COLS, vals))
    factor_pairs.sort(key=lambda x: -abs(x[1]))
    return [{"feature": f, "shap_value": round(float(v), 4)} for f, v in factor_pairs[:top_n]]

def run_prediction(row_vals):
    input_df = pd.DataFrame([{f: float(row_vals.get(f, 0)) for f in FEATURE_COLS}])[FEATURE_COLS]
    scaled = scaler.transform(input_df)
    pred = model.predict(scaled)[0]
    prob = float(model.predict_proba(scaled)[0][1])
    score_100 = round(prob * 100, 1)
    severity, color = severity_tier(score_100)
    factors = get_shap_factors(input_df)
    return {
        "prediction": "INSIDER" if pred == 1 else "Normal",
        "risk_score": round(prob, 4),
        "risk_score_100": score_100,
        "severity": severity,
        "severity_color": color,
        "top_factors": factors,
        "raw_input": row_vals
    }

@app.route("/")
def index():
    return render_template("dashboard.html", fields=MANUAL_FIELDS)

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json(force=True) or {}
        result = run_prediction(data)
        return jsonify(result)
    except Exception as ex:
        return jsonify({"error": str(ex)}), 400

@app.route("/export/pdf", methods=["POST"])
def export_pdf():
    try:
        data = request.get_json(force=True) or {}
        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=letter)
        width, height = letter

        c.setFillColorRGB(0.04, 0.06, 0.12)
        c.rect(0, height-80, width, 80, fill=1)
        c.setFillColorRGB(1, 1, 1)
        c.setFont("Helvetica-Bold", 18)
        c.drawString(50, height-45, "InsightGuard — Investigation Report")
        c.setFont("Helvetica", 10)
        c.drawString(50, height-65, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        y = height - 120
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, f"Prediction: {data.get('prediction','N/A')}")
        y -= 25
        c.drawString(50, y, f"Risk Score: {data.get('risk_score_100','N/A')}/100 ({data.get('severity','N/A')} Severity)")
        y -= 35

        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "Top Contributing Factors (SHAP):")
        y -= 20
        c.setFont("Helvetica", 10)
        for f in data.get("top_factors", []):
            c.drawString(60, y, f"- {f['feature']}: {f['shap_value']}")
            y -= 16

        y -= 20
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "Raw Input Values:")
        y -= 20
        c.setFont("Helvetica", 9)
        for k, v in data.get("raw_input", {}).items():
            c.drawString(60, y, f"{k}: {v}")
            y -= 14
            if y < 60:
                c.showPage()
                y = height - 60

        c.save()
        buf.seek(0)
        return send_file(buf, mimetype='application/pdf', as_attachment=True, download_name='investigation_report.pdf')
    except Exception as ex:
        return jsonify({"error": str(ex)}), 400

if __name__ == "__main__":
    import os
    port = int(os.getenv("FLASK_PORT", 5000))
    ngrok_token = os.getenv("NGROK_AUTH_TOKEN")
    if ngrok_token:
        from pyngrok import ngrok, conf
        conf.get_default().auth_token = ngrok_token
        ngrok.kill()
        tunnel = ngrok.connect(f"127.0.0.1:{port}")
        print(f"Public URL: {tunnel.public_url}")
    app.run(host="127.0.0.1", port=port, debug=False)
