"""
===============================================================================
Service       : Live Individual Employee Threat Analyzer Service
File          : backend/services/live_threat_analyzer_service.py
Project       : Insider Threat Behavioral Intelligence System / SentinelAI

Description   :
    Evaluates live custom employee feature vectors through the existing
    pre-trained ML model artifacts (scaler.pkl + 7 models) and CERT Layer 2
    behavioral vector validation against enterprise population baselines.

    DOES NOT retrain models.
    DOES NOT alter CERT datasets or parquet files.
===============================================================================
"""

from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import logging
import numpy as np
import pandas as pd
import joblib

from backend.services.verification_service import (
    _load_and_merge_datasets,
    _compute_population_baselines,
    _calculate_percentile,
    _safe_float,
    _safe_int,
    DISCLAIMER_TEXT,
)

logger = logging.getLogger(__name__)

# =============================================================================
# Authoritative Feature Schema Contract (22 Canonical Features)
# =============================================================================

CANONICAL_FEATURE_SCHEMA = [
    {"name": "total_events", "type": float, "min": 0, "max": 1000000, "category": "Volume & Activity", "label": "Total Events"},
    {"name": "active_days", "type": float, "min": 1, "max": 1000, "category": "Volume & Activity", "label": "Active Days"},
    {"name": "unique_pcs", "type": float, "min": 1, "max": 1000, "category": "Multi-PC & Access", "label": "Unique PCs"},
    {"name": "unique_sources", "type": float, "min": 1, "max": 100, "category": "Multi-PC & Access", "label": "Unique Sources"},
    {"name": "total_logins", "type": float, "min": 0, "max": 50000, "category": "Temporal Activity", "label": "Total Logins"},
    {"name": "midnight_activity", "type": float, "min": 0, "max": 50000, "category": "Temporal Activity", "label": "Midnight Activity"},
    {"name": "after_hours_activity", "type": float, "min": 0, "max": 50000, "category": "Temporal Activity", "label": "After-Hours Activity"},
    {"name": "weekend_activity", "type": float, "min": 0, "max": 50000, "category": "Temporal Activity", "label": "Weekend Activity"},
    {"name": "device_events", "type": float, "min": 0, "max": 50000, "category": "Device / USB Activity", "label": "USB Device Connects"},
    {"name": "file_events", "type": float, "min": 0, "max": 50000, "category": "Device / USB Activity", "label": "File Copy Events"},
    {"name": "unique_files", "type": float, "min": 0, "max": 50000, "category": "Device / USB Activity", "label": "Unique File Copies"},
    {"name": "emails_sent", "type": float, "min": 0, "max": 50000, "category": "Email Activity", "label": "Emails Sent"},
    {"name": "web_events", "type": float, "min": 0, "max": 500000, "category": "Web Activity", "label": "Web HTTP Requests"},
    {"name": "unique_urls", "type": float, "min": 0, "max": 50000, "category": "Web Activity", "label": "Unique URLs Visited"},
    {"name": "average_hour", "type": float, "min": 0.0, "max": 24.0, "category": "Temporal Activity", "label": "Average Activity Hour"},
    {"name": "earliest_hour", "type": float, "min": 0.0, "max": 24.0, "category": "Temporal Activity", "label": "Earliest Activity Hour"},
    {"name": "latest_hour", "type": float, "min": 0.0, "max": 24.0, "category": "Temporal Activity", "label": "Latest Activity Hour"},
    {"name": "openness", "type": float, "min": 0.0, "max": 100.0, "category": "Psychometrics", "label": "Openness Score"},
    {"name": "conscientiousness", "type": float, "min": 0.0, "max": 100.0, "category": "Psychometrics", "label": "Conscientiousness Score"},
    {"name": "extraversion", "type": float, "min": 0.0, "max": 100.0, "category": "Psychometrics", "label": "Extraversion Score"},
    {"name": "agreeableness", "type": float, "min": 0.0, "max": 100.0, "category": "Psychometrics", "label": "Agreeableness Score"},
    {"name": "neuroticism", "type": float, "min": 0.0, "max": 100.0, "category": "Psychometrics", "label": "Neuroticism Score"},
]

CANONICAL_FEATURE_NAMES = [f["name"] for f in CANONICAL_FEATURE_SCHEMA]

# =============================================================================
# Model Artifact Loader Cache
# =============================================================================

_cached_models: Optional[Dict[str, Any]] = None


def get_loaded_models() -> Dict[str, Any]:
    """
    Loads saved model artifacts once and caches them in memory.
    """
    global _cached_models
    if _cached_models is not None:
        return _cached_models

    model_dir = Path(__file__).resolve().parents[2] / "models"
    loaded = {}

    scaler_file = model_dir / "scaler.pkl"
    if scaler_file.exists():
        loaded["scaler"] = joblib.load(scaler_file)
    else:
        raise FileNotFoundError(f"Scaler artifact missing at {scaler_file}")

    model_files = [
        ("isolation_forest", "isolation_forest.pkl"),
        ("one_class_svm", "one_class_svm.pkl"),
        ("lof", "lof.pkl"),
        ("elliptic_envelope", "elliptic_envelope.pkl"),
        ("pca", "pca.pkl"),
        ("dbscan", "dbscan.pkl"),
        ("kmeans", "kmeans.pkl"),
    ]

    for key, fname in model_files:
        fpath = model_dir / fname
        if fpath.exists():
            loaded[key] = joblib.load(fpath)
        else:
            logger.warning(f"Model artifact {fname} not found in {model_dir}")

    _cached_models = loaded
    return _cached_models


# =============================================================================
# Feature Validation
# =============================================================================

def validate_and_align_features(raw_features: Dict[str, Any]) -> Tuple[pd.DataFrame, Dict[str, float]]:
    """
    Validates input feature dict, checks for missing/invalid/extra features,
    and returns a aligned 1-row DataFrame matching CANONICAL_FEATURE_NAMES.
    """
    if not isinstance(raw_features, dict):
        raise ValueError("Features payload must be a JSON object / dictionary.")

    aligned_dict = {}
    
    # Check for invalid feature data types
    for key, val in raw_features.items():
        if key not in CANONICAL_FEATURE_NAMES:
            # Allow metadata keys if passed inside features
            if key in ["user", "user_id", "name", "employee_id", "department", "role", "email"]:
                continue
            raise ValueError(f"Unknown or unauthorized feature encountered: '{key}'")
        
        if val is None or isinstance(val, bool):
            raise ValueError(f"Feature '{key}' must be a numeric value, received: {val}")
        try:
            float_val = float(val)
            if np.isnan(float_val) or np.isinf(float_val):
                raise ValueError(f"Feature '{key}' must be a finite number.")
            aligned_dict[key] = float_val
        except (ValueError, TypeError):
            raise ValueError(f"Feature '{key}' has non-numeric value: '{val}'")

    # Ensure all canonical features are present (defaulting missing to 0.0)
    final_vector = {}
    for item in CANONICAL_FEATURE_SCHEMA:
        fname = item["name"]
        val = aligned_dict.get(fname, 0.0)
        
        # Min boundary check
        if "min" in item and val < item["min"]:
            raise ValueError(f"Feature '{fname}' value {val} is below minimum allowed ({item['min']})")
        
        final_vector[fname] = val

    # Create 1-row dataframe in exact column order
    df_row = pd.DataFrame([final_vector], columns=CANONICAL_FEATURE_NAMES)
    return df_row, final_vector


# =============================================================================
# Risk Score Calculation (Authoritative Boundaries)
# =============================================================================

def calculate_risk_score_and_level(consensus_pct: float, anomalous_vector_count: int, max_vectors: int = 6) -> Tuple[float, str]:
    """
    Calculates 0.0-100.0 risk score and maps to authoritative boundaries:
      0.0  - 24.9 -> LOW
     25.0  - 49.9 -> MEDIUM
     50.0  - 74.9 -> HIGH
     75.0 - 100.0 -> CRITICAL
    """
    # Base vector evidence score (0-50) + Model consensus score (0-50)
    vector_ratio = min(1.0, max(0.0, anomalous_vector_count / float(max_vectors)))
    vector_score = vector_ratio * 50.0
    model_score = (consensus_pct / 100.0) * 50.0
    
    raw_score = round(vector_score + model_score, 1)
    risk_score = min(100.0, max(0.0, raw_score))

    if risk_score >= 75.0:
        risk_level = "CRITICAL"
    elif risk_score >= 50.0:
        risk_level = "HIGH"
    elif risk_score >= 25.0:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return risk_score, risk_level


# =============================================================================
# Core Live Inference Routine
# =============================================================================

def analyze_live_employee_threat(
    employee_id: str,
    raw_features: Dict[str, Any],
    employee_name: Optional[str] = None,
    department: Optional[str] = None,
    role: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Evaluates an employee's feature vector live against the 7 trained ML models
    and CERT Layer 2 behavioral pattern baselines.
    """
    # 1. Align & validate features
    df_feat, clean_features = validate_and_align_features(raw_features)

    # 2. Load model artifacts
    artifacts = get_loaded_models()
    scaler = artifacts["scaler"]
    X_scaled = scaler.transform(df_feat)

    # 3. Handle 7 Models Inference
    model_results = []
    models_triggered_count = 0
    models_evaluated_count = 0

    # Model 1: Isolation Forest
    if "isolation_forest" in artifacts:
        mdl = artifacts["isolation_forest"]
        pred = mdl.predict(X_scaled)[0]
        is_susp = (pred == -1)
        score = float(mdl.decision_function(X_scaled)[0]) if hasattr(mdl, "decision_function") else None
        model_results.append({
            "model_name": "Isolation Forest",
            "prediction": "Suspicious" if is_susp else "Normal",
            "status": "suspicious" if is_susp else "normal",
            "anomaly_score": score,
            "inference_status": "success",
            "explanation": "Partition-based outlier isolation" if is_susp else "Within expected behavioral density"
        })
        models_evaluated_count += 1
        if is_susp: models_triggered_count += 1

    # Model 2: One-Class SVM
    if "one_class_svm" in artifacts:
        mdl = artifacts["one_class_svm"]
        pred = mdl.predict(X_scaled)[0]
        is_susp = (pred == -1)
        score = float(mdl.decision_function(X_scaled)[0]) if hasattr(mdl, "decision_function") else None
        model_results.append({
            "model_name": "One-Class SVM",
            "prediction": "Suspicious" if is_susp else "Normal",
            "status": "suspicious" if is_susp else "normal",
            "anomaly_score": score,
            "inference_status": "success",
            "explanation": "Boundary deviation from normal profile" if is_susp else "Lies within normal boundary"
        })
        models_evaluated_count += 1
        if is_susp: models_triggered_count += 1

    # Model 3: LOF
    if "lof" in artifacts:
        mdl = artifacts["lof"]
        if hasattr(mdl, "predict"):
            pred = mdl.predict(X_scaled)[0]
            is_susp = (pred == -1)
            score = float(mdl.score_samples(X_scaled)[0]) if hasattr(mdl, "score_samples") else None
            model_results.append({
                "model_name": "Local Outlier Factor (LOF)",
                "prediction": "Suspicious" if is_susp else "Normal",
                "status": "suspicious" if is_susp else "normal",
                "anomaly_score": score,
                "inference_status": "success",
                "explanation": "Lower density than local neighborhood" if is_susp else "Dense peer neighborhood similarity"
            })
            models_evaluated_count += 1
            if is_susp: models_triggered_count += 1

    # Model 4: Elliptic Envelope
    if "elliptic_envelope" in artifacts:
        mdl = artifacts["elliptic_envelope"]
        pred = mdl.predict(X_scaled)[0]
        is_susp = (pred == -1)
        score = float(mdl.decision_function(X_scaled)[0]) if hasattr(mdl, "decision_function") else None
        model_results.append({
            "model_name": "Elliptic Envelope",
            "prediction": "Suspicious" if is_susp else "Normal",
            "status": "suspicious" if is_susp else "normal",
            "anomaly_score": score,
            "inference_status": "success",
            "explanation": "Mahalanobis distance outlier" if is_susp else "Within robust Gaussian covariance envelope"
        })
        models_evaluated_count += 1
        if is_susp: models_triggered_count += 1

    # Model 5: PCA Reconstruction Error
    if "pca" in artifacts:
        pca = artifacts["pca"]
        reconstructed = pca.inverse_transform(pca.transform(X_scaled))
        rec_error = float(np.mean(np.square(X_scaled - reconstructed)))
        # 97th percentile reconstruction error threshold from training (07_model_training.py line 575: P97 = 0.176865)
        pca_p97_threshold = 0.176865
        is_susp = rec_error >= pca_p97_threshold
        model_results.append({
            "model_name": "PCA",
            "prediction": "Suspicious" if is_susp else "Normal",
            "status": "suspicious" if is_susp else "normal",
            "anomaly_score": rec_error,
            "inference_status": "success",
            "explanation": f"Reconstruction error ({rec_error:.4f}) exceeds P97 training baseline ({pca_p97_threshold})" if is_susp else "Low reconstruction error"
        })
        models_evaluated_count += 1
        if is_susp: models_triggered_count += 1

    # Model 6: DBSCAN (Density-Based Spatial Clustering)
    if "dbscan" in artifacts:
        # DBSCAN does not support direct predict() on new unseen points in scikit-learn
        model_results.append({
            "model_name": "DBSCAN",
            "prediction": "Not Directly Inferable",
            "status": "not_inferable",
            "anomaly_score": None,
            "inference_status": "not_directly_inferable",
            "explanation": "DBSCAN is a density clustering model and does not support out-of-sample prediction for new unseen feature vectors."
        })

    # Model 7: K-Means Centroid Distance
    if "kmeans" in artifacts:
        km = artifacts["kmeans"]
        min_dist = float(np.min(km.transform(X_scaled)))
        # 97th percentile centroid distance threshold from training (07_model_training.py line 695: P97 = 6.325461)
        kmeans_p97_threshold = 6.325461
        is_susp = min_dist >= kmeans_p97_threshold
        model_results.append({
            "model_name": "K-Means",
            "prediction": "Suspicious" if is_susp else "Normal",
            "status": "suspicious" if is_susp else "normal",
            "anomaly_score": min_dist,
            "inference_status": "success",
            "explanation": f"Centroid distance ({min_dist:.2f}) exceeds P97 training radius ({kmeans_p97_threshold:.2f})" if is_susp else "Clustered near normal centroid"
        })
        models_evaluated_count += 1
        if is_susp: models_triggered_count += 1

    # Model Consensus
    consensus_percentage = round((models_triggered_count / 7.0) * 100.0, 2)

    # 4. CERT Layer 2 Verification & Peer Group Baseline Percentile Comparison
    pop_df = _load_and_merge_datasets()
    baselines = _compute_population_baselines(pop_df)

    # Calculate 6 Behavioral Dimensions
    temporal_val = clean_features["after_hours_activity"] + clean_features["midnight_activity"] + clean_features["weekend_activity"]
    device_val = clean_features["device_events"] + clean_features["file_events"]
    pc_val = clean_features["unique_pcs"]
    web_val = clean_features["web_events"]
    email_val = clean_features["emails_sent"]
    volume_val = clean_features["total_events"]

    p1 = round(_calculate_percentile(baselines["pop_offhours"], temporal_val), 1)
    p2 = round(_calculate_percentile(baselines["pop_device"], device_val), 1)
    p3 = round(_calculate_percentile(baselines["pop_pcs"], pc_val), 1)
    p4 = round(_calculate_percentile(baselines["pop_web"], web_val), 1)
    p5 = round(_calculate_percentile(baselines["pop_email"], email_val), 1)
    p6 = round(_calculate_percentile(baselines["pop_events"], volume_val), 1)

    anomalous_vectors = []
    vector_evidence = []

    if temporal_val >= baselines["p1_p90"] and temporal_val > 50:
        anomalous_vectors.append("Temporal Activity")
        vector_evidence.append(f"Off-hours/weekend events ({int(temporal_val):,}) in {p1}th percentile vs population median ({baselines['p1_median']:.1f})")

    if device_val >= baselines["p2_p90"] and device_val > 0:
        anomalous_vectors.append("Device / USB Activity")
        vector_evidence.append(f"USB/file events ({int(device_val):,}) in {p2}th percentile vs population 90th percentile ({baselines['p2_p90']:.1f})")

    if pc_val >= baselines["p3_p90"] and pc_val > 2:
        anomalous_vectors.append("Multi-PC Access")
        vector_evidence.append(f"Logged into {int(pc_val)} distinct machines ({p3}th percentile) vs population median ({baselines['p3_median']:.1f})")

    if web_val >= baselines["p4_p90"] and web_val > 500:
        anomalous_vectors.append("Web Activity")
        vector_evidence.append(f"HTTP web requests ({int(web_val):,}) in {p4}th percentile vs population median ({baselines['p4_median']:.1f})")

    if email_val >= baselines["p5_p90"] and email_val > 100:
        anomalous_vectors.append("Email Activity")
        vector_evidence.append(f"Emails sent ({int(email_val):,}) in {p5}th percentile vs population median ({baselines['p5_median']:.1f})")

    if volume_val >= baselines["p6_p90"] and volume_val > 1000:
        anomalous_vectors.append("Overall Behavioral Volume")
        vector_evidence.append(f"Total events ({int(volume_val):,}) in {p6}th percentile vs population median ({baselines['p6_median']:.1f})")

    anomalous_count = len(anomalous_vectors)

    # 5. Risk Score & Level calculation
    risk_score, risk_level = calculate_risk_score_and_level(consensus_percentage, anomalous_count)

    layer2_verification = {
        "disclaimer": DISCLAIMER_TEXT,
        "validation_status": "Behaviorally Supported" if (anomalous_count >= 2 and models_triggered_count >= 2) else "Lacks Behavioral Support",
        "supported_by_behavioral_evidence": anomalous_count >= 2 and models_triggered_count >= 2,
        "anomalous_vectors_count": anomalous_count,
        "total_vectors_tested": 6,
        "anomalous_vectors": anomalous_vectors,
        "vector_percentiles": {
            "temporal": p1,
            "device": p2,
            "multi_pc": p3,
            "web": p4,
            "email": p5,
            "overall_volume": p6,
        }
    }

    if not vector_evidence:
        vector_evidence.append("All behavioral activity metrics remain within normal population baselines.")

    return {
        "employee": {
            "employee_id": employee_id,
            "employee_name": employee_name or f"Employee ({employee_id})",
            "department": department or "General",
            "role": role or "Staff",
        },
        "model_results": model_results,
        "models_evaluated": 7,
        "models_inferable": models_evaluated_count,
        "models_triggered": models_triggered_count,
        "consensus_percentage": consensus_percentage,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "layer2_verification": layer2_verification,
        "behavioral_evidence": vector_evidence,
        "raw_features": clean_features,
        "inference_status": "success"
    }
