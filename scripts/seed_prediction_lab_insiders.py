"""Seed 50 High and 50 Critical synthetic insiders for the Prediction Lab.

Run from the project root:
    python scripts/seed_prediction_lab_insiders.py

The script is idempotent: re-running it refreshes the synthetic activity and
latest RiskScore for the same 100 employees rather than creating duplicates.
"""
import os
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models import ActivityLog, ActivityType, Department, Employee, RiskCategory, RiskScore


HIGH_COUNT = 50
CRITICAL_COUNT = 50


def make_log(employee_id, activity_type, timestamp, resource, bytes_transferred=0):
    return ActivityLog(
        employee_id=employee_id,
        activity_type=activity_type,
        timestamp=timestamp,
        source_ip=f"10.42.{employee_id % 250}.17",
        destination_ip="198.51.100.24",
        resource=resource,
        bytes_transferred=bytes_transferred,
        duration_seconds=900,
        is_outside_hours=True,
        is_suspicious=True,
        # device_id is an integer foreign key; the resource identifies the
        # synthetic external device without requiring a Device row.
        device_id=None,
        raw_log={"synthetic": True, "source": "prediction_lab_insider_seed"},
    )


def add_activity(db, employee, level, now):
    """Create feature-rich recent activity that also scores high with fallback ML."""
    db.query(ActivityLog).filter(
        ActivityLog.employee_id == employee.id,
        ActivityLog.raw_log["source"].as_string() == "prediction_lab_insider_seed",
    ).delete(synchronize_session=False)

    logs = []
    if level == "critical":
        # Multiple severe signals: credential attacks, admin abuse, USB and cloud exfiltration.
        for offset in range(10):
            ts = now - timedelta(days=offset % 7, hours=2, minutes=offset)
            logs.extend([
                make_log(employee.id, ActivityType.failed_login, ts, "vpn-gateway"),
                make_log(employee.id, ActivityType.privilege_change, ts + timedelta(minutes=2), "prod_db/admin_grant"),
                make_log(employee.id, ActivityType.usb_connect, ts + timedelta(minutes=4), "USBSTOR/EXTERNAL-DRIVE"),
                make_log(employee.id, ActivityType.file_download, ts + timedelta(minutes=6), "prod_db/confidential_export.zip", 75 * 1024 * 1024),
                make_log(employee.id, ActivityType.file_upload, ts + timedelta(minutes=8), "s3.amazonaws.com/exfiltration", 125 * 1024 * 1024),
                make_log(employee.id, ActivityType.database_query, ts + timedelta(minutes=10), "SELECT * FROM prod_db.credentials"),
            ])
    else:
        # Sustained but less severe signals: off-hours VPN, failed logins and USB/file activity.
        for offset in range(6):
            ts = now - timedelta(days=offset, hours=3, minutes=offset)
            logs.extend([
                make_log(employee.id, ActivityType.failed_login, ts, "vpn-gateway"),
                make_log(employee.id, ActivityType.remote_access, ts + timedelta(minutes=3), "vpn-gateway"),
                make_log(employee.id, ActivityType.usb_connect, ts + timedelta(minutes=6), "USBSTOR/EXTERNAL-DRIVE"),
                make_log(employee.id, ActivityType.file_download, ts + timedelta(minutes=9), "finance/confidential-report.xlsx", 30 * 1024 * 1024),
                make_log(employee.id, ActivityType.database_query, ts + timedelta(minutes=12), "SELECT * FROM prod_db.payroll"),
            ])
    db.add_all(logs)


def upsert_risk_score(db, employee, level, now):
    is_critical = level == "critical"
    score = 94.0 if is_critical else 68.0
    category = RiskCategory.critical if is_critical else RiskCategory.high
    label = "Critical Risk" if is_critical else "High Risk"
    explanation = {
        "is_insider": True,
        "insider_status": "INSIDER THREAT DETECTED",
        "confidence": 96.0 if is_critical else 89.0,
        "shap_explanation": (
            "Synthetic critical insider pattern: credential attacks, privilege escalation, "
            "external storage, and cloud exfiltration."
            if is_critical else
            "Synthetic high-risk insider pattern: repeated off-hours VPN access, failed logins, "
            "external storage, and sensitive database access."
        ),
        "recommended_action": "Open an insider-threat investigation and preserve endpoint evidence.",
        "top_factors": [
            {"factor": "Failed Logins", "score": 10 if is_critical else 6, "weight": "35%"},
            {"factor": "Privilege Escalation", "score": 10 if is_critical else 0, "weight": "30%"},
            {"factor": "Data Transfer Size", "score": 2000 if is_critical else 180, "weight": "25%"},
        ],
        "class_probabilities": {
            "Normal": 0.01, "Low Risk": 0.01, "Medium Risk": 0.03,
            "High Risk": 0.15 if is_critical else 0.80,
            "Critical Risk": 0.80 if is_critical else 0.15,
        },
    }
    score_row = (
        db.query(RiskScore)
        .filter(RiskScore.employee_id == employee.id)
        .order_by(RiskScore.score_date.desc())
        .first()
    )
    if score_row is None:
        score_row = RiskScore(employee_id=employee.id, total_score=score, risk_category=category)
        db.add(score_row)
    score_row.total_score = score
    score_row.risk_category = category
    score_row.behavioral_anomaly_score = score
    score_row.privilege_misuse_score = 95.0 if is_critical else 45.0
    score_row.data_access_violation_score = 95.0 if is_critical else 65.0
    score_row.access_pattern_score = 90.0 if is_critical else 70.0
    score_row.historical_security_score = explanation["confidence"]
    score_row.isolation_forest_score = score
    score_row.xgboost_probability = explanation["confidence"] / 100
    score_row.trend = "increasing"
    score_row.explanation = explanation
    score_row.score_date = now


def seed_prediction_lab_insiders():
    db = SessionLocal()
    try:
        department = db.query(Department).filter(Department.code == "SEC").first()
        if department is None:
            department = Department(name="IT Security", code="SEC", description="Synthetic-data security cohort")
            db.add(department)
            db.flush()

        now = datetime.now(timezone.utc)
        created = {"high": 0, "critical": 0}
        for level, count, prefix in (("high", HIGH_COUNT, "SYN-H"), ("critical", CRITICAL_COUNT, "SYN-C")):
            for number in range(1, count + 1):
                code = f"{prefix}-{number:03d}"
                employee = db.query(Employee).filter(Employee.employee_id == code).first()
                if employee is None:
                    employee = Employee(
                        employee_id=code,
                        full_name=f"Synthetic {level.title()} Insider {number:03d}",
                        email=f"{code.lower()}@synthetic.example",
                        designation="Security Analyst",
                        department_id=department.id,
                        access_level="privileged",
                        is_active=True,
                        hire_date=now - timedelta(days=365),
                    )
                    db.add(employee)
                    db.flush()
                    created[level] += 1
                add_activity(db, employee, level, now)
                upsert_risk_score(db, employee, level, now)

        db.commit()
        print(f"Prediction Lab insider data ready: {HIGH_COUNT} High + {CRITICAL_COUNT} Critical employees.")
        print(f"New employees created: High={created['high']}, Critical={created['critical']}")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_prediction_lab_insiders()
