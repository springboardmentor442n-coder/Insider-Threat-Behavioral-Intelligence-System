"""
Training Pipeline for Hybrid Insider Threat Detection Engine
=============================================================
Trains:
  1. Isolation Forest for unsupervised anomaly detection
  2. XGBoost for supervised risk classification
Saves fitted models, scalers, and encoders.
"""
import os
import sys
import numpy as np
import pandas as pd
import joblib
from datetime import datetime, timezone
from typing import Dict, Tuple
from loguru import logger

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split

from app.core.database import SessionLocal
from app.core.config import settings
from app.models import Employee, ActivityLog
from app.ml.feature_engineering import extract_features, FEATURE_NAMES, N_FEATURES

MODEL_DIR = settings.MODEL_PATH
os.makedirs(MODEL_DIR, exist_ok=True)

# Risk categories requested: Normal, Low Risk, Medium Risk, High Risk, Critical Risk
RISK_CLASSES = [
    "Normal",
    "Low Risk",
    "Medium Risk",
    "High Risk",
    "Critical Risk"
]

CERT_SCENARIO_LABEL_MAP = {
    "O": "Unauthorized Access",
    "F": "Data Exfiltration",
    "S": "IT Sabotage",
    "I": "Intellectual Property Theft",
    "E": "Data Exfiltration",
}

CERT_TO_RISK_MAP = {
    "Normal": "Normal",
    "Unauthorized Access": "Medium Risk",
    "Intellectual Property Theft": "High Risk",
    "Data Exfiltration": "High Risk",
    "IT Sabotage": "Critical Risk",
}


def generate_synthetic_samples(n_samples_per_class: int = 80) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate synthetic samples for the 20 features to bootstrap the XGBoost model.
    This guarantees that the model has multi-class calibration even before logs are loaded.
    More samples per class = better generalization and diverse predictions.
    """
    X_syn = []
    y_syn = []

    np.random.seed(42)

    for i in range(n_samples_per_class):
        # 1. Normal
        normal = [
            np.random.normal(9.0, 1.0),      # login_time (average login hour)
            np.random.poisson(0.1),         # failed_logins
            np.random.poisson(0.2),         # vpn_usage
            np.random.poisson(0.1),         # usb_usage
            np.random.normal(2.0, 1.0),      # file_downloads
            np.random.normal(1.0, 0.5),      # file_uploads
            np.random.normal(5.0, 2.0),      # email_count
            np.random.poisson(0.05),        # cloud_uploads
            np.random.choice([1.0, 2.0]),    # device_changes
            np.random.uniform(0.0, 0.1),     # working_hours (off-hours ratio)
            0.0,                             # privilege_escalation
            np.random.poisson(0.2),         # database_access
            np.random.normal(8.0, 3.0),      # website_visits
            np.random.poisson(0.1),         # external_storage_usage
            np.random.randint(1, 4),         # location
            np.random.randint(1, 6),         # department
            np.random.randint(1, 8),         # role
            np.random.normal(28800.0, 3600), # session_duration (8 hours)
            np.random.normal(1.0, 0.2),      # login_frequency
            np.random.normal(15.0, 5.0)      # data_transfer_size (MB)
        ]
        X_syn.append(normal)
        y_syn.append("Normal")

        # 2. Low Risk
        low = [
            np.random.normal(10.0, 1.5),
            np.random.poisson(0.3),
            np.random.poisson(0.5),
            np.random.poisson(0.3),
            np.random.normal(4.0, 2.0),
            np.random.normal(2.0, 1.0),
            np.random.normal(8.0, 3.0),
            np.random.poisson(0.2),
            np.random.choice([1.0, 2.0]),
            np.random.uniform(0.05, 0.15),
            0.0,
            np.random.poisson(0.5),
            np.random.normal(12.0, 4.0),
            np.random.poisson(0.3),
            np.random.randint(1, 4),
            np.random.randint(1, 6),
            np.random.randint(1, 8),
            np.random.normal(30000.0, 4000),
            np.random.normal(1.2, 0.3),
            np.random.normal(25.0, 10.0)
        ]
        X_syn.append(low)
        y_syn.append("Low Risk")

        # 3. Medium Risk
        med = [
            np.random.normal(12.0, 2.5),
            np.random.poisson(1.5),          # higher failed logins
            np.random.poisson(2.0),          # higher VPN usage
            np.random.poisson(1.2),          # higher USB usage
            np.random.normal(10.0, 4.0),     # higher file downloads
            np.random.normal(5.0, 2.0),      # higher file uploads
            np.random.normal(15.0, 5.0),
            np.random.poisson(1.0),          # cloud uploads
            np.random.choice([2.0, 3.0]),    # device changes
            np.random.uniform(0.15, 0.35),   # higher off-hours ratio
            0.0,
            np.random.poisson(3.0),          # database queries
            np.random.normal(25.0, 8.0),
            np.random.poisson(1.5),
            np.random.randint(1, 4),
            np.random.randint(1, 6),
            np.random.randint(1, 8),
            np.random.normal(35000.0, 5000),
            np.random.normal(2.0, 0.5),
            np.random.normal(120.0, 40.0)    # 120 MB
        ]
        X_syn.append(med)
        y_syn.append("Medium Risk")

        # 4. High Risk
        high = [
            np.random.normal(15.0, 3.5),
            np.random.poisson(3.0),          # failed logins
            np.random.poisson(5.0),          # VPN usages
            np.random.poisson(3.5),          # USB connections
            np.random.normal(25.0, 8.0),     # downloads
            np.random.normal(15.0, 5.0),     # uploads
            np.random.normal(30.0, 10.0),
            np.random.poisson(4.0),          # cloud uploads
            np.random.choice([3.0, 4.0]),    # multiple devices
            np.random.uniform(0.35, 0.60),   # high off hours
            np.random.poisson(0.5),          # possible privilege changes
            np.random.poisson(8.0),          # database access
            np.random.normal(50.0, 15.0),
            np.random.poisson(4.0),          # external storage
            np.random.randint(1, 4),
            np.random.randint(1, 6),
            np.random.randint(1, 8),
            np.random.normal(45000.0, 8000),
            np.random.normal(3.5, 0.8),
            np.random.normal(450.0, 150.0)   # 450 MB data transfer
        ]
        X_syn.append(high)
        y_syn.append("High Risk")

        # 5. Critical Risk
        crit = [
            np.random.normal(19.0, 4.0),     # weird hours
            np.random.poisson(6.0),          # high failed logins
            np.random.poisson(8.0),          # vpn
            np.random.poisson(7.0),          # usb
            np.random.normal(65.0, 15.0),    # massive downloads
            np.random.normal(40.0, 12.0),    # massive uploads
            np.random.normal(60.0, 20.0),
            np.random.poisson(8.0),          # cloud uploads
            np.random.choice([4.0, 5.0]),    # device changes
            np.random.uniform(0.60, 0.95),   # critical off-hours
            np.random.poisson(2.5),          # privilege escalations!
            np.random.poisson(20.0),         # high database access
            np.random.normal(100.0, 30.0),
            np.random.poisson(8.0),          # external storage exfil
            np.random.randint(1, 4),
            np.random.randint(1, 6),
            np.random.randint(1, 8),
            np.random.normal(60000.0, 12000),
            np.random.normal(5.0, 1.5),
            np.random.normal(1500.0, 400.0)  # 1.5 GB data transfer
        ]
        X_syn.append(crit)
        y_syn.append("Critical Risk")

    return np.array(X_syn, dtype=np.float32), np.array(y_syn)


def build_training_dataset(
    db,
    malicious_users: Dict[str, str],
    feature_window: int = 30,
) -> Tuple[np.ndarray, np.ndarray]:
    """Build dataset from DB employees combined with synthetic bootstrapping."""
    employees = db.query(Employee).filter(Employee.is_active == True).all()
    logger.info(f"Building dataset for {len(employees)} database employees ...")

    X_db, y_db = [], []
    skipped = 0

    for emp in employees:
        features = extract_features(db, emp.id, days=feature_window)

        if features.sum() == 0:
            skipped += 1
            continue

        cert_label = (
            malicious_users.get(emp.employee_id) or
            malicious_users.get(emp.email.split("@")[0]) or
            malicious_users.get(emp.email) or
            "Normal"
        )
        risk_label = CERT_TO_RISK_MAP.get(cert_label, "Normal")
        X_db.append(features)
        y_db.append(risk_label)

    logger.info(f"Database contains: {len(X_db)} active samples ({skipped} empty skipped)")

    # Bootstrap with synthetic samples to ensure robust multiclass outputs
    X_syn, y_syn = generate_synthetic_samples()

    if X_db:
        X_all = np.vstack([np.array(X_db), X_syn])
        y_all = np.concatenate([np.array(y_db), y_syn])
    else:
        X_all = X_syn
        y_all = y_syn

    return X_all, y_all


def train(
    malicious_users: Dict[str, str] = None,
    config: Dict = None,
) -> Dict:
    """Trains StandardScaler, LabelEncoder, Isolation Forest, and XGBoost Classifier."""
    cfg = {
        "epochs": 100,
        "feature_window": 30,
        "seed": 42
    }
    if config:
        cfg.update(config)

    np.random.seed(cfg["seed"])

    db = SessionLocal()
    try:
        malicious = malicious_users or {}
        X, y_str = build_training_dataset(db, malicious, cfg["feature_window"])
    finally:
        db.close()

    # Fit Label Encoder
    encoder = LabelEncoder()
    encoder.fit(RISK_CLASSES)
    y = encoder.transform(y_str)

    # Fit StandardScaler
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X).astype(np.float32)

    # Split for model validation
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=cfg["seed"], stratify=y
    )

    # Train RandomForestClassifier (supervised risk prediction and behavioral profiling)
    classifier = RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        random_state=cfg["seed"],
        n_jobs=-1
    )
    classifier.fit(X_train, y_train)

    # Save all objects
    scaler_path = os.path.join(MODEL_DIR, "pipeline_scaler.pkl")
    encoder_path = os.path.join(MODEL_DIR, "target_label_encoder.pkl")
    classifier_path = os.path.join(MODEL_DIR, "classifier_model.pkl")

    joblib.dump(scaler, scaler_path)
    joblib.dump(encoder, encoder_path)
    joblib.dump(classifier, classifier_path)

    logger.info(f"✅ Saved scaler → {scaler_path}")
    logger.info(f"✅ Saved encoder → {encoder_path}")
    logger.info(f"✅ Saved Classifier → {classifier_path}")

    # Reload into inference service
    from app.ml import inference as inf_service
    inf_service.load_model()

    return {
        "status": "success",
        "classes": list(encoder.classes_),
        "n_samples": len(X),
        "model_paths": {
            "scaler": scaler_path,
            "encoder": encoder_path,
            "classifier": classifier_path
        },
        "trained_at": datetime.now(timezone.utc).isoformat()
    }


if __name__ == "__main__":
    result = train()
    print("\n=== Hybrid Training Complete ===")
    for k, v in result.items():
        print(f"  {k}: {v}")
