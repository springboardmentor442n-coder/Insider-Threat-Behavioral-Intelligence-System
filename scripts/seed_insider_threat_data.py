"""
Unified Insider Threat Data Seeder
===================================
Seeds realistic suspicious activity logs, anomalies, and matching ML risk scores
for employee accounts to ensure complete data consistency across:
- ML Inference page
- Prediction Lab (Pipeline Scan)
- Activity Logs page
- Anomalies page
- Risk Scores page
"""
import sys
import os
import random
from datetime import datetime, timezone, timedelta

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models import (
    Employee, ActivityLog, ActivityType, Anomaly, AnomalyType,
    RiskScore, RiskCategory, Alert, AlertSeverity, AlertStatus
)
from app.ml import inference as inf_service

random.seed(42)

def seed_insider_threat_data():
    db = SessionLocal()
    try:
        employees = db.query(Employee).all()
        if not employees:
            print("❌ No employees found in database.")
            return

        print(f"🔄 Processing {len(employees)} employees...")

        # 1. Designate ~15% of employees as Insiders, ~20% as High Risk, ~30% as Medium Risk, rest Low Risk
        total = len(employees)
        n_critical = max(1, int(total * 0.12))
        n_high = max(1, int(total * 0.18))
        n_medium = max(1, int(total * 0.30))

        shuffled = list(employees)
        random.shuffle(shuffled)

        critical_emps = shuffled[:n_critical]
        high_emps = shuffled[n_critical:n_critical + n_high]
        medium_emps = shuffled[n_critical + n_high:n_critical + n_high + n_medium]
        low_emps = shuffled[n_critical + n_high + n_medium:]

        now = datetime.now(timezone.utc)

        # Helper to generate suspicious logs for an employee
        def add_suspicious_logs(emp, category):
            days_back = random.randint(1, 28)
            log_time = now - timedelta(days=days_back, hours=random.randint(1, 23))

            if category == "critical":
                # Critical Insider: Multiple severe indicators (failed logins, privilege change, USB, exfiltration)
                logs_data = [
                    (ActivityType.login, "Failed Login Attempt", "Multiple failed password attempts detected from suspicious IP", True, True, 0, "10.0.9.15"),
                    (ActivityType.failed_login, "Failed Login", "Brute force pattern detected", True, True, 0, "10.0.9.15"),
                    (ActivityType.failed_login, "Failed Login", "Brute force pattern detected", True, True, 0, "10.0.9.15"),
                    (ActivityType.privilege_change, "Privilege Escalation", "Granted unauthorized admin rights to local group", True, True, 0, "192.168.1.50"),
                    (ActivityType.usb_connect, "USB Connected", "External high-capacity storage drive connected", True, True, 0, "USBSTOR\\DISK&VEN_SANDISK"),
                    (ActivityType.file_download, "Bulk Download", "Downloaded 450 confidential engineering schematics", True, True, 250 * 1024 * 1024, "confidential_blueprint_v2.pdf"),
                    (ActivityType.file_upload, "Cloud Upload", "Uploaded archive to external cloud host (s3.amazonaws.com)", True, True, 450 * 1024 * 1024, "s3.amazonaws.com/backup_exfil.zip"),
                    (ActivityType.database_query, "Database Query", "SELECT * FROM prod_db.users_credentials", True, True, 15 * 1024 * 1024, "prod_db.users"),
                ]
            elif category == "high":
                # High Risk: Failed logins, off-hours access, USB
                logs_data = [
                    (ActivityType.failed_login, "Failed Login", "Repeated login failure outside business hours", True, True, 0, "192.168.1.99"),
                    (ActivityType.remote_access, "VPN Session", "Off-hours VPN connection established from unusual location", True, True, 0, "VPN-GW-01"),
                    (ActivityType.usb_connect, "USB Drive Connected", "USB storage device attached", True, True, 0, "USBSTOR\\DISK"),
                    (ActivityType.file_download, "File Download", "Downloaded sensitive financial report", True, False, 45 * 1024 * 1024, "Q3_financial_report.xlsx"),
                    (ActivityType.application_access, "DB Access", "Accessed production database console", True, True, 5 * 1024 * 1024, "prod_db_analytics"),
                ]
            elif category == "medium":
                # Medium Risk: Minor off-hours or file downloads
                logs_data = [
                    (ActivityType.login, "Login", "Standard login during off-hours", True, False, 0, "192.168.1.20"),
                    (ActivityType.file_download, "File Download", "Downloaded project documentation", False, False, 12 * 1024 * 1024, "project_notes.docx"),
                    (ActivityType.network_access, "Web Browsing", "Visited external file sharing website", False, False, 2 * 1024 * 1024, "filetransfer.io"),
                ]
            else:
                # Low Risk / Normal: Standard business activity
                logs_data = [
                    (ActivityType.login, "Login", "Successful morning login", False, False, 0, "192.168.1.10"),
                    (ActivityType.email_send, "Email Sent", "Sent email to internal team", False, False, 100 * 1024, "team@company.com"),
                ]

            for act_type, name, desc, off_hours, susp, bytes_tx, res in logs_data:
                log = ActivityLog(
                    employee_id=emp.id,
                    activity_type=act_type,
                    timestamp=log_time + timedelta(minutes=random.randint(1, 120)),
                    source_ip=f"192.168.1.{10 + emp.id % 200}",
                    destination_ip="192.168.1.1",
                    resource=res,
                    bytes_transferred=bytes_tx,
                    duration_seconds=random.randint(30, 1800),
                    is_outside_hours=off_hours,
                    is_suspicious=susp,
                    device_id=f"DEV-{emp.employee_id}",
                    raw_log={"seeded": True, "name": name, "description": desc}
                )
                db.add(log)

            # Create Anomaly record if High or Critical
            if category in ["critical", "high"]:
                anom_type = AnomalyType.usb_exfiltration if category == "critical" else AnomalyType.off_hours_activity
                anom = Anomaly(
                    employee_id=emp.id,
                    anomaly_type=anom_type,
                    severity=AlertSeverity.critical if category == "critical" else AlertSeverity.high,
                    score=random.uniform(75.0, 95.0) if category == "critical" else random.uniform(55.0, 74.0),
                    detected_at=log_time,
                    description=f"Behavioral anomaly detected for {emp.full_name}: {category.upper()} risk pattern identified.",
                    details={"category": category, "employee_code": emp.employee_id}
                )
                db.add(anom)

        print("📝 Seeding activity logs and anomalies for critical, high, and medium employees...")

        for emp in critical_emps:
            add_suspicious_logs(emp, "critical")

        for emp in high_emps:
            add_suspicious_logs(emp, "high")

        for emp in medium_emps:
            add_suspicious_logs(emp, "medium")

        for emp in low_emps[:50]:  # Seed sample low logs
            add_suspicious_logs(emp, "low")

        db.commit()
        print("✅ Activity logs & Anomalies created.")

        # 2. Recompute and save RiskScores using ML Inference Engine for ALL employees
        print("🤖 Computing ML Risk Scores via RandomForest Inference Engine...")

        # Clear old RiskScore and Alert records to maintain exact sync
        from sqlalchemy import text
        db.execute(text("UPDATE alerts SET risk_score_id = NULL WHERE risk_score_id IS NOT NULL"))
        db.commit()
        db.query(Alert).delete()
        db.query(RiskScore).delete()
        db.commit()

        scores_created = 0
        cat_counts = {}

        for emp in employees:
            pred = inf_service.predict_employee(db, emp.id, days=30)
            score = pred["threat_score"]
            level_str = pred["threat_level"]

            cat_map = {
                "Normal": RiskCategory.low,
                "Low Risk": RiskCategory.low,
                "Medium Risk": RiskCategory.medium,
                "High Risk": RiskCategory.high,
                "Critical Risk": RiskCategory.critical
            }
            category = cat_map.get(level_str, RiskCategory.low)
            cat_counts[category.value] = cat_counts.get(category.value, 0) + 1

            explanation = {
                "top_factors": [
                    {"factor": tf["feature"].replace("_", " ").title(), "score": round(tf["value"], 2), "weight": f"{tf['contribution']*100:.1f}%"}
                    for tf in pred["top_features"]
                ],
                "shap_explanation": pred["shap_explanation"],
                "recommended_action": pred["recommended_action"],
                "confidence": pred["confidence"],
                "is_insider": pred["is_insider"],
                "insider_status": pred["insider_status"],
                "class_probabilities": pred["class_probabilities"]
            }

            rs = RiskScore(
                employee_id=emp.id,
                behavioral_anomaly_score=pred["isolation_forest_score"],
                privilege_misuse_score=float(pred["feature_values"].get("privilege_escalation", 0.0) * 20),
                data_access_violation_score=float(pred["feature_values"].get("data_transfer_size", 0.0) / 10),
                access_pattern_score=float(pred["feature_values"].get("usb_usage", 0.0) * 15),
                historical_security_score=pred["confidence"],
                total_score=score,
                risk_category=category,
                trend="increasing" if category in [RiskCategory.high, RiskCategory.critical] else "stable",
                explanation=explanation,
                isolation_forest_score=pred["isolation_forest_score"],
                xgboost_probability=pred["confidence"] / 100.0,
                score_date=now - timedelta(hours=random.randint(0, 48))
            )
            db.add(rs)
            scores_created += 1

            # Auto-create alert if High or Critical
            if category in (RiskCategory.high, RiskCategory.critical):
                alert = Alert(
                    alert_id=f"ALT-{emp.employee_id}-{random.randint(100, 999)}",
                    employee_id=emp.id,
                    title=f"🚨 INSIDER THREAT DETECTED: {emp.full_name} ({emp.employee_id})",
                    description=f"{pred['insider_status']}: {pred['shap_explanation']} | Score: {score:.1f}",
                    severity=AlertSeverity.critical if category == RiskCategory.critical else AlertSeverity.high,
                    status=AlertStatus.open,
                    triggered_at=now
                )
                db.add(alert)

        db.commit()

        print("\n" + "=" * 55)
        print(f"✅ UNIFIED INSIDER THREAT DATA SEEDED ({scores_created} Employees)")
        print("=" * 55)
        for cat, cnt in cat_counts.items():
            print(f"  {cat.upper():15s}: {cnt:4d} employees")
        print("=" * 55)

    except Exception as e:
        print(f"❌ Error seeding insider threat data: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_insider_threat_data()
