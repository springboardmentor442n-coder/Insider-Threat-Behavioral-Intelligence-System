import os, pickle
import pandas as pd
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from feature_engineering import engineer_features, attach_ldap_context

load_dotenv()

MODEL_DIR = "model"

def _load(name):
    with open(os.path.join(MODEL_DIR, name), "rb") as f:
        return pickle.load(f)

model = _load("model.pkl")
scaler = _load("scaler.pkl")
FEATURE_COLS = _load("feature_columns.pkl")
le_dict = _load("le_dict.pkl")

app = Flask(__name__)

def predict_batch(combined_df):
    X = combined_df[FEATURE_COLS].fillna(0)
    X_scaled = scaler.transform(X)
    preds = model.predict(X_scaled)
    probs = model.predict_proba(X_scaled)[:, 1]
    results = []
    for i, (_, row) in enumerate(combined_df.iterrows()):
        results.append({
            "user": str(row["user"]),
            "date": str(row["day"]),
            "prediction": "INSIDER" if preds[i] == 1 else "Normal",
            "risk_score": round(float(probs[i]), 4)
        })
    return results

@app.route("/")
def index():
    return render_template("dashboard.html")

@app.route("/health")
def health():
    return jsonify({"status": "ok", "model_loaded": model is not None})

@app.route("/predict", methods=["POST"])
def predict_single():
    try:
        row = request.get_json(force=True) or {}
        input_dict = {f: float(row.get(f, 0)) for f in FEATURE_COLS}
        input_df = pd.DataFrame([input_dict])[FEATURE_COLS]
        scaled = scaler.transform(input_df)
        pred = model.predict(scaled)[0]
        prob = model.predict_proba(scaled)[0][1]
        return jsonify({
            "prediction": "INSIDER" if pred == 1 else "Normal",
            "risk_score": round(float(prob), 4)
        })
    except Exception as ex:
        return jsonify({"error": str(ex)}), 400

@app.route("/predict_csv", methods=["POST"])
def predict_csv():
    try:
        required = ["logon", "device", "file", "email", "http"]
        missing = [r for r in required if r not in request.files]
        if missing:
            return jsonify({"error": f"Missing files: {missing}"}), 400

        logon = pd.read_csv(request.files["logon"])
        device = pd.read_csv(request.files["device"])
        file_df = pd.read_csv(request.files["file"])
        email = pd.read_csv(request.files["email"])
        http = pd.read_csv(request.files["http"])

        combined = engineer_features(logon, device, file_df, email, http)

        if "ldap" in request.files:
            ldap_df = pd.read_csv(request.files["ldap"])
            combined = attach_ldap_context(combined, ldap_df, le_dict)
        else:
            for col in ["role_encoded", "department_encoded", "team_encoded", "supervisor_encoded"]:
                combined[col] = 0

        results = predict_batch(combined)
        flagged = [r for r in results if r["prediction"] == "INSIDER"]
        return jsonify({"total_rows": len(results), "flagged_count": len(flagged), "results": results})
    except Exception as ex:
        return jsonify({"error": str(ex)}), 400

if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", 5000))
    ngrok_token = os.getenv("NGROK_AUTH_TOKEN")
    if ngrok_token:
        from pyngrok import ngrok, conf
        conf.get_default().auth_token = ngrok_token
        ngrok.kill()
        tunnel = ngrok.connect(f"127.0.0.1:{port}")
        print(f"Public URL: {tunnel.public_url}")
    app.run(host="127.0.0.1", port=port, debug=False)
