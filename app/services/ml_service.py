"""
ML Service — Behavioral Profiling, Anomaly Detection, Risk Scoring.
Orchestrates training and predictions using hybrid models.
"""
import os
import numpy as np
import pandas as pd
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from loguru import logger

from app.core.config import settings
from app.models import (
    Employee, ActivityLog, BehavioralProfile, Anomaly, RiskScore,
    RiskCategory, AnomalyType, ActivityType, Alert, AlertSeverity, AlertStatus
)

os.makedirs(settings.MODEL_PATH, exist_ok=True)


# ─── Module 4: Behavioral Profiling ──────────────────────────────────────────
def build_behavioral_profile(db: Session, employee_id: int, days: int = 60) -> BehavioralProfile:
    """Compute baseline statistics from past `days` of activity."""
    since = datetime.now(timezone.utc) - timedelta(days=days)
    logs = (db.query(ActivityLog)
            .filter(ActivityLog.employee_id == employee_id,
                    ActivityLog.timestamp >= since)
            .all())

    profile = db.query(BehavioralProfile).filter(
        BehavioralProfile.employee_id == employee_id).first()
    if not profile:
        profile = BehavioralProfile(employee_id=employee_id)
        db.add(profile)
        db.commit()

    if not logs:
        return profile

    df = pd.DataFrame([{
        "date": l.timestamp.date(),
        "hour": l.timestamp.hour,
        "activity_type": l.activity_type.value,
        "bytes": l.bytes_transferred or 0,
        "is_outside_hours": l.is_outside_hours,
        "source_ip": l.source_ip or "",
    } for l in logs])

    # Per-day aggregates
    daily = df.groupby("date").agg(
        logins=("activity_type", lambda x: (x == "login").sum()),
        file_ops=("activity_type", lambda x: x.isin(["file_download","file_upload","data_transfer"]).sum()),
        total_bytes=("bytes", "sum"),
        email_count=("activity_type", lambda x: x.isin(["email_send","email_receive"]).sum()),
        app_count=("activity_type", lambda x: (x == "application_access").sum()),
    ).reset_index()

    # Work hour distribution
    hour_counts = df["hour"].value_counts().to_dict()
    peak_hours = sorted(hour_counts, key=hour_counts.get, reverse=True)[:8]
    work_hours = {"peak_hours": peak_hours, "off_hours_pct": float(df["is_outside_hours"].mean())}

    # Typical IPs
    top_ips = df["source_ip"].value_counts().head(10).index.tolist()

    n_days = max(1, (df["date"].max() - df["date"].min()).days + 1)

    profile.avg_daily_logins = float(daily["logins"].mean())
    profile.std_daily_logins = float(daily["logins"].std() or 0)
    profile.avg_daily_file_accesses = float(daily["file_ops"].mean())
    profile.std_daily_file_accesses = float(daily["file_ops"].std() or 0)
    profile.avg_daily_data_transfer_mb = float(daily["total_bytes"].mean() / 1_048_576)
    profile.std_daily_data_transfer_mb = float((daily["total_bytes"].std() or 0) / 1_048_576)
    profile.avg_daily_email_count = float(daily["email_count"].mean())
    profile.avg_daily_app_count = float(daily["app_count"].mean())
    profile.work_hours_baseline = work_hours
    profile.typical_source_ips = top_ips
    profile.baseline_days = n_days
    profile.last_updated = datetime.now(timezone.utc)

    db.commit()
    db.refresh(profile)
    logger.info(f"Behavioral profile built for employee {employee_id} ({n_days} days of data)")
    return profile


# ─── Module 5: Anomaly Detection ─────────────────────────────────────────────
def train_isolation_forest(db: Session):
    """Trigger the global training script."""
    from app.ml.train import train
    return train()


def detect_anomalies(db: Session, employee_id: int, days: int = 1) -> List[Anomaly]:
    """Run anomaly detection based on Isolation Forest model."""
    from app.ml import inference as inf_service

    if not inf_service.is_model_loaded():
        logger.warning("Models not loaded — anomaly detection skipped")
        return []

    try:
        pred = inf_service.predict_employee(db, employee_id, days=days)
    except Exception as e:
        logger.error(f"Anomaly prediction failed for employee {employee_id}: {e}")
        return []

    anomalies_created = []

    # If Isolation Forest detects high anomalies, log it
    if pred["isolation_forest_level"] in ("Suspicious", "Critical"):
        score = pred["isolation_forest_score"] / 100.0
        desc = f"Isolation Forest detected behavior anomaly: {pred['shap_explanation']}"
        anomaly = Anomaly(
            employee_id=employee_id,
            anomaly_type=AnomalyType.peer_deviation,
            anomaly_score=round(score, 4),
            description=desc,
            features=pred["feature_values"],
            model_name="isolation_forest",
            detected_at=datetime.now(timezone.utc)
        )
        db.add(anomaly)
        db.commit()
        db.refresh(anomaly)
        anomalies_created.append(anomaly)
        logger.info(f"Anomaly logged for employee {employee_id} (score={score:.2f})")

    return anomalies_created


# ─── Module 6: Risk Scoring ───────────────────────────────────────────────────
def compute_risk_score(db: Session, employee_id: int) -> RiskScore:
    """Fuses Isolation Forest and XGBoost predictions into a unified RiskScore."""
    from app.ml import inference as inf_service

    if not inf_service.is_model_loaded():
        raise RuntimeError("Models not loaded — call load_model() first")

    # Run predictions
    pred = inf_service.predict_employee(db, employee_id, days=30)
    total = pred["threat_score"]

    cat_map = {
        "Normal": RiskCategory.low,
        "Low Risk": RiskCategory.low,
        "Medium Risk": RiskCategory.medium,
        "High Risk": RiskCategory.high,
        "Critical Risk": RiskCategory.critical
    }
    category = cat_map.get(pred["threat_level"], RiskCategory.low)

    # Compute trend
    prev = (db.query(RiskScore)
            .filter(RiskScore.employee_id == employee_id)
            .order_by(RiskScore.score_date.desc())
            .first())
    if prev:
        delta = total - prev.total_score
        trend = "increasing" if delta > 5 else "decreasing" if delta < -5 else "stable"
    else:
        trend = "stable"

    explanation = {
        "top_factors": [
            {"factor": tf["feature"].replace("_", " ").title(), "score": round(tf["value"], 2), "weight": f"{tf['contribution']*100:.1f}%"}
            for tf in pred["top_features"]
        ],
        "shap_explanation": pred["shap_explanation"],
        "recommended_action": pred["recommended_action"],
        "confidence": pred["confidence"]
    }

    rs = RiskScore(
        employee_id=employee_id,
        behavioral_anomaly_score=pred["isolation_forest_score"],
        privilege_misuse_score=float(pred["feature_values"].get("privilege_escalation", 0.0) * 20),
        data_access_violation_score=float(pred["feature_values"].get("data_transfer_size", 0.0) / 10),
        access_pattern_score=float(pred["feature_values"].get("usb_usage", 0.0) * 15),
        historical_security_score=pred["confidence"],
        total_score=total,
        risk_category=category,
        trend=trend,
        explanation=explanation,
        isolation_forest_score=pred["isolation_forest_score"],
        xgboost_probability=pred["confidence"],
        score_date=datetime.now(timezone.utc)
    )

    db.add(rs)
    db.commit()
    db.refresh(rs)

    logger.info(f"Risk score computed for employee {employee_id}: {total:.1f} [{category}]")
    return rs


# ─── Batch recalculation ─────────────────────────────────────────────────────
def run_daily_scoring(db: Session):
    """Orchestrates daily scoring logic: baselines, anomalies, and risk fusion."""
    employees = db.query(Employee).filter(Employee.is_active == True).all()
    logger.info(f"Daily scoring run: {len(employees)} active employees")

    for emp in employees:
        try:
            build_behavioral_profile(db, emp.id)
            detect_anomalies(db, emp.id, days=1)
            rs = compute_risk_score(db, emp.id)
            # Auto-generate alerts if risk level is critical or high
            if rs.risk_category in (RiskCategory.high, RiskCategory.critical):
                _auto_create_alert(db, emp.id, rs)
        except Exception as e:
            logger.error(f"Daily scoring failed for employee {emp.id}: {e}")


def _auto_create_alert(db: Session, employee_id: int, rs: RiskScore):
    """Auto creates structured alert logs based on risk features."""
    from app.ml import inference as inf_service

    # Get the latest prediction characteristics
    pred = inf_service.predict_employee(db, employee_id, days=30)
    features = pred["feature_values"]

    # Match alert types
    title = "Critical Threat"
    if features.get("usb_usage", 0.0) > 0.0:
        title = "USB Device Inserted"
    elif features.get("database_access", 0.0) > 5.0:
        title = "Unauthorized Database Access"
    elif features.get("failed_logins", 0.0) > 3.0:
        title = "Multiple Failed Logins"
    elif features.get("privilege_escalation", 0.0) > 0.0:
        title = "Privilege Abuse"
    elif features.get("working_hours", 0.0) > 0.4:
        title = "Abnormal Login"
    elif features.get("data_transfer_size", 0.0) > 100.0:
        title = "Massive Data Download"
    elif features.get("cloud_uploads", 0.0) > 0.0:
        title = "Cloud Data Leakage"
    elif features.get("vpn_usage", 0.0) > 3.0:
        title = "Suspicious VPN"
    elif features.get("email_count", 0.0) > 10.0:
        title = "Email Exfiltration"

    severity = AlertSeverity.critical if rs.risk_category == RiskCategory.critical else AlertSeverity.high
    alert_id = f"ALT-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{employee_id:04d}"

    existing = db.query(Alert).filter(Alert.alert_id == alert_id).first()
    if existing:
        return

    desc = (
        f"Insider risk score reached {rs.total_score:.1f} [{rs.risk_category}]. "
        f"AI Explanation: {pred['shap_explanation']}. "
        f"Recommended Action: {pred['recommended_action']}"
    )

    alert = Alert(
        alert_id=alert_id,
        title=title,
        description=desc,
        severity=severity,
        status=AlertStatus.open,
        employee_id=employee_id,
        risk_score_id=rs.id,
        triggered_at=datetime.now(timezone.utc),
        notes=f"AI Recommendation: {pred['recommended_action']}"
    )
    db.add(alert)
    db.commit()
    logger.info(f"Alert created: {title} for employee {employee_id}")
