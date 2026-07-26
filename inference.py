"""
Model Inference Service - Hybrid Risk Scoring Engine
===================================================
Combines Isolation Forest and XGBoost predictions using a Risk Fusion Engine.
Utilizes SHAP for explainable AI predictions and recommended actions.
"""
import os
import numpy as np
import joblib
from datetime import datetime, timezone
from typing import Dict, List, Tuple
from loguru import logger

from app.core.config import settings
from app.ml.feature_engineering import extract_features, FEATURE_NAMES

MODEL_DIR = settings.MODEL_PATH

RISK_CLASSES = ["Normal", "Low Risk", "Medium Risk", "High Risk", "Critical Risk"]
CLASS_LABELS = RISK_CLASSES

# Models
_scaler = None
_encoder = None
_iforest = None
_xgb = None
_explainer = None  # SHAP TreeExplainer

# Load SHAP gracefully
SHAP_OK = False
try:
    import shap
    SHAP_OK = True
except ImportError:
    logger.warning("SHAP not installed — using analytical fallback for explainability")


def load_model():
    """Load Scaler, LabelEncoder, Isolation Forest, and XGBoost models."""
    global _scaler, _encoder, _iforest, _xgb, _explainer

    scaler_path = os.path.join(MODEL_DIR, "pipeline_scaler.pkl")
    encoder_path = os.path.join(MODEL_DIR, "target_label_encoder.pkl")
    iforest_path = os.path.join(MODEL_DIR, "isolation_forest.pkl")
    xgboost_path = os.path.join(MODEL_DIR, "xgboost_model.pkl")

    if os.path.exists(scaler_path):
        _scaler = joblib.load(scaler_path)
        logger.info("✅ StandardScaler loaded")

    if os.path.exists(encoder_path):
        _encoder = joblib.load(encoder_path)
        logger.info("✅ LabelEncoder loaded")

    if os.path.exists(iforest_path):
        _iforest = joblib.load(iforest_path)
        logger.info("✅ Isolation Forest loaded")

    if os.path.exists(xgboost_path):
        _xgb = joblib.load(xgboost_path)
        logger.info("✅ XGBoost Classifier loaded")

        if SHAP_OK:
            try:
                # Pre-initialize explainer for fast inference
                _explainer = shap.TreeExplainer(_xgb)
                logger.info("✅ SHAP TreeExplainer initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize SHAP explainer: {e}")
                _explainer = None


def _compute_heuristic_score(feature_vector: np.ndarray) -> Dict:
    """
    Rule-based fallback when models are not loaded.
    Critically: sparse feature vectors (new/quiet employees) map to Normal/Low,
    NOT Critical Risk. Only high-value risky indicators push to higher levels.
    """
    failed_logins = float(feature_vector[1])
    vpn_usage = float(feature_vector[2])
    usb_usage = float(feature_vector[3])
    downloads = float(feature_vector[4])
    uploads = float(feature_vector[5])
    off_hours = float(feature_vector[9])
    privilege = float(feature_vector[10])
    db_access = float(feature_vector[11])
    exfil_mb = float(feature_vector[19])

    # Start at 5.0 (normal baseline) — sparse/no activity stays near 5
    score = 5.0
    score += failed_logins * 8.0
    score += vpn_usage * 2.0
    score += usb_usage * 5.0
    score += privilege * 20.0
    score += max(db_access - 2.0, 0.0) * 4.0
    score += off_hours * 15.0
    score += min(exfil_mb / 50.0, 15.0)
    score += min(downloads / 20.0, 10.0)
    score += min(uploads / 10.0, 8.0)

    final_score = min(max(score, 3.0), 97.0)

    if final_score >= 75.0:
        threat_level = "Critical Risk"
    elif final_score >= 50.0:
        threat_level = "High Risk"
    elif final_score >= 25.0:
        threat_level = "Medium Risk"
    elif final_score >= 12.0:
        threat_level = "Low Risk"
    else:
        threat_level = "Normal"

    # Build uniform probability distribution (model not loaded)
    class_probs = {}
    for c in RISK_CLASSES:
        class_probs[c] = 0.2

    top_features = []
    for name, val in zip(FEATURE_NAMES, feature_vector):
        top_features.append({
            "feature": name,
            "value": float(val),
            "contribution": 0.05 if val > 0 else -0.02
        })
    top_features.sort(key=lambda x: x["value"], reverse=True)
    top_features = top_features[:5]

    reasons = ["Heuristic assessment (model not trained yet)."]
    if privilege > 0:
        reasons.append("Privilege change registered.")
    if usb_usage > 0:
        reasons.append("USB connect logged.")
    if db_access > 3:
        reasons.append("Frequent database queries.")

    return {
        "threat_score": final_score,
        "threat_level": threat_level,
        "confidence": 60.0,
        "isolation_forest_score": min(final_score * 0.9, 100.0),
        "isolation_forest_level": "Normal" if final_score < 30 else "Suspicious" if final_score < 60 else "Critical",
        "xgboost_prediction": threat_level,
        "class_probabilities": class_probs,
        "top_features": top_features,
        "shap_explanation": " | ".join(reasons),
        "recommended_action": "Train the model via the ML Calibration Console for calibrated predictions.",
        "predicted_at": datetime.now(timezone.utc).isoformat()
    }


def predict_threat(feature_vector: np.ndarray) -> Dict:
    """
    Run hybrid inference on a 20-dim feature vector.
    Fuses Isolation Forest and XGBoost predictions.
    """
    if _scaler is None or _iforest is None or _xgb is None:
        return _compute_heuristic_score(feature_vector)

    # Reshape and scale feature vector
    vector_reshaped = feature_vector.reshape(1, -1)
    scaled = _scaler.transform(vector_reshaped)

    # 1. Isolation Forest Component
    iforest_raw = _iforest.decision_function(scaled)[0]
    # Map decision function [-0.5, 0.5] to [0, 100] anomaly score (higher = anomaly)
    iforest_score = float(min(max((0.4 - iforest_raw) * 100, 0.0), 100.0))

    iforest_level = "Normal"
    if iforest_score >= 70.0:
        iforest_level = "Critical"
    elif iforest_score >= 40.0:
        iforest_level = "Suspicious"

    # 2. XGBoost Component
    probs = _xgb.predict_proba(scaled)[0]  # Array of 5 class probabilities
    pred_idx = int(np.argmax(probs))
    pred_label = _encoder.classes_[pred_idx] if _encoder else "Normal"
    confidence = float(probs[pred_idx])  # Already in 0-1 range

    # Map XGBoost class order to risk scores
    # Encoder sorts alphabetically: Critical Risk(0), High Risk(1), Low Risk(2), Medium Risk(3), Normal(4)
    # We need to compute a weighted risk score using the correct class-score mapping
    class_score_map = {}
    if _encoder is not None:
        for i, cls in enumerate(_encoder.classes_):
            if cls == "Normal":
                class_score_map[i] = 5.0
            elif cls == "Low Risk":
                class_score_map[i] = 22.0
            elif cls == "Medium Risk":
                class_score_map[i] = 45.0
            elif cls == "High Risk":
                class_score_map[i] = 72.0
            elif cls == "Critical Risk":
                class_score_map[i] = 92.0
    else:
        class_score_map = {0: 92.0, 1: 72.0, 2: 22.0, 3: 45.0, 4: 5.0}

    xgb_risk_score = float(sum(probs[i] * class_score_map.get(i, 0.0) for i in range(len(probs))))

    # 3. Risk Fusion Engine
    # Final Risk Score = 0.4 * Isolation Forest + 0.6 * XGBoost Risk Score
    final_score = float(round(0.4 * iforest_score + 0.6 * xgb_risk_score, 2))

    # Threat Level based on Fusion Score
    if final_score >= 75.0:
        threat_level = "Critical Risk"
    elif final_score >= 50.0:
        threat_level = "High Risk"
    elif final_score >= 25.0:
        threat_level = "Medium Risk"
    elif final_score >= 12.0:
        threat_level = "Low Risk"
    else:
        threat_level = "Normal"

    # 4. SHAP and Analytical Explainability
    shap_vals = None
    if _explainer is not None and SHAP_OK:
        try:
            # Get SHAP values for class index `pred_idx` (or positive threat classes)
            all_shap = _explainer.shap_values(scaled)
            # For multi-class, shape can be (nsamples, nfeatures, nclasses) or list of classes
            if isinstance(all_shap, list):
                shap_vals = all_shap[pred_idx][0]
            else:
                shap_vals = all_shap[0, :, pred_idx]
        except Exception as e:
            logger.debug(f"SHAP values computation failed, using analytical fallback: {e}")
            shap_vals = None

    # Analytical fallback if SHAP failed or is disabled
    if shap_vals is None:
        importances = _xgb.feature_importances_
        deviations = scaled[0]
        shap_vals = deviations * importances

    # Build Top Features list
    feature_contributions = []
    for name, raw_val, shap_val in zip(FEATURE_NAMES, feature_vector, shap_vals):
        feature_contributions.append({
            "feature": name,
            "value": float(round(raw_val, 2)),
            "contribution": float(round(shap_val, 4))
        })

    # Sort by contribution (absolute or positive magnitude)
    feature_contributions.sort(key=lambda x: x["contribution"], reverse=True)
    top_features = feature_contributions[:5]

    # 5. Natural Language SHAP Explanation & Actions
    reasons = []
    actions = []

    for tf in top_features:
        f_name = tf["feature"]
        val = tf["value"]
        if tf["contribution"] > 0.01:
            if f_name == "failed_logins" and val > 0:
                reasons.append(f"Multiple failed logins detected ({val:.0f} occurrences)")
                actions.append("Verify employee identity and check for potential credential stuffing/brute force.")
            elif f_name == "working_hours" and val > 0.3:
                reasons.append(f"Significant off-hours activity ({val*100:.0f}% outside standard hours)")
                actions.append("Review employee working schedule; check for unauthorized nocturnal logins.")
            elif f_name == "usb_usage" and val > 0:
                reasons.append(f"USB storage device connected ({val:.0f} connect events)")
                actions.append("Ensure connected USB devices comply with Corporate Data Loss Prevention (DLP) policies.")
            elif f_name == "file_downloads" and val > 10:
                reasons.append(f"High volume of file downloads ({val:.0f} downloaded items)")
                actions.append("Audit downloaded items; ensure files are not intellectual property blueprints.")
            elif f_name == "privilege_escalation" and val > 0:
                reasons.append(f"Privilege change attempt recorded ({val:.0f} occurrences)")
                actions.append("Investigate permissions; check if administrator rights were temporarily granted or abused.")
            elif f_name == "database_access" and val > 5:
                reasons.append(f"Abnormal database query accesses ({val:.0f} queries)")
                actions.append("Audit SQL queries; check if sensitive tables (e.g. users, payroll) were accessed.")
            elif f_name == "cloud_uploads" and val > 0:
                reasons.append(f"Data upload to public cloud drives detected ({val:.0f} events)")
                actions.append("Block unauthorized cloud storage hosts; inspect file content for data leakage.")
            elif f_name == "vpn_usage" and val > 3:
                reasons.append(f"Abnormal VPN remote access frequency ({val:.0f} sessions)")
                actions.append("Confirm login source IPs match employee geolocation records.")
            elif f_name == "data_transfer_size" and val > 100:
                reasons.append(f"Large volume of outbound data transfer ({val:.1f} MB)")
                actions.append("Trigger active DLP containment protocol; isolate host if exfiltration is confirmed.")

    if not reasons:
        reasons.append("Behavior mostly correlates with the department baseline, with minor variations.")
        actions.append("Continue standard automated baseline monitoring.")

    explanation_str = " | ".join(reasons)
    recommended_action = actions[0] if actions else "No action required. Maintain baseline monitoring."

    # Build class probabilities dict using encoder class names
    class_probs = {}
    if _encoder is not None:
        for i in range(len(probs)):
            class_probs[_encoder.classes_[i]] = float(round(probs[i], 4))
    else:
        for i, c in enumerate(RISK_CLASSES):
            class_probs[c] = float(round(probs[i] if i < len(probs) else 0.2, 4))

    return {
        "threat_score": final_score,
        "threat_level": threat_level,
        "confidence": float(round(confidence * 100.0, 1)),  # Convert 0-1 → percentage once
        "isolation_forest_score": float(round(iforest_score, 2)),
        "isolation_forest_level": iforest_level,
        "xgboost_prediction": pred_label,
        "class_probabilities": class_probs,
        "top_features": top_features,
        "shap_explanation": explanation_str,
        "recommended_action": recommended_action,
        "predicted_at": datetime.now(timezone.utc).isoformat()
    }


def predict_employee(db, employee_id: int, days: int = 30) -> Dict:
    """Full prediction pipeline: extract features → predict."""
    features = extract_features(db, employee_id, days=days)
    result = predict_threat(features)
    result["employee_id"] = employee_id
    result["feature_window_days"] = days
    result["feature_values"] = {
        name: round(float(val), 4)
        for name, val in zip(FEATURE_NAMES, features)
    }
    return result


def is_model_loaded() -> bool:
    global _scaler, _iforest, _xgb
    if _scaler is None or _iforest is None or _xgb is None:
        try:
            load_model()
        except Exception as e:
            logger.warning(f"Dynamic model reload attempt failed: {e}")
    return _scaler is not None and _iforest is not None and _xgb is not None
