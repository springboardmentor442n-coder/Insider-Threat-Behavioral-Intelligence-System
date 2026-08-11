import os
import random
import pandas as pd
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.risk_record import BehavioralRiskRecord
from app.models.alert import SecurityAlert
from app.models.investigation import Investigation, AuditLog
from app.core.security import get_password_hash
from app.core.config import settings
from app.ml.predictor import predictor_service

HIGH_RISK_USERS_LIST = ["DLM0051", "THR0873", "GKO0078", "JCG0316", "MOH0273", "LAP0338", "LRR0148", "IRM0931"]

def seed_initial_data(db: Session):
    # 1. Seed Default Analyst and Admin Users
    if db.query(User).count() == 0:
        admin = User(
            username="admin",
            email="admin@cybersecurity.corp",
            full_name="SOC Admin",
            hashed_password=get_password_hash("admin123"),
            role="admin"
        )
        analyst = User(
            username="analyst",
            email="analyst@cybersecurity.corp",
            full_name="Lead Security Analyst",
            hashed_password=get_password_hash("analyst123"),
            role="analyst"
        )
        db.add(admin)
        db.add(analyst)
        db.commit()
        print("Database: Initial admin and analyst users created.")

    # 2. Seed Behavioral Risk Records
    if db.query(BehavioralRiskRecord).count() == 0:
        if os.path.exists(settings.RISK_RESULTS_CSV):
            print(f"Database: Loading existing dataset from {settings.RISK_RESULTS_CSV}...")
            df = pd.read_csv(settings.RISK_RESULTS_CSV)
            records = []
            for _, row in df.iterrows():
                rec = BehavioralRiskRecord(
                    user=str(row.get("user", "")),
                    day=str(row.get("day", "")),
                    logon_count=int(row.get("logon_count", 0)),
                    logoff_count=int(row.get("logoff_count", 0)),
                    off_hours_logons=int(row.get("off_hours_logons", 0)),
                    unique_pcs=int(row.get("unique_pcs", 0)),
                    device_connects=int(row.get("device_connects", 0)),
                    device_disconnects=int(row.get("device_disconnects", 0)),
                    unique_device_pcs=int(row.get("unique_device_pcs", 0)),
                    file_activity_count=int(row.get("file_activity_count", 0)),
                    unique_file_pcs=int(row.get("unique_file_pcs", 0)),
                    unique_files=int(row.get("unique_files", 0)),
                    sensitive_file_count=int(row.get("sensitive_file_count", 0)),
                    email_count=int(row.get("email_count", 0)),
                    attachment_count=int(row.get("attachment_count", 0)),
                    total_email_size=float(row.get("total_email_size", 0.0)),
                    unique_email_pcs=int(row.get("unique_email_pcs", 0)),
                    external_email_count=int(row.get("external_email_count", 0)),
                    http_request_count=int(row.get("http_request_count", 0)),
                    unique_http_urls=int(row.get("unique_http_urls", 0)),
                    off_hours_http=int(row.get("off_hours_http", 0)),
                    prediction=int(row.get("prediction", 0)),
                    prediction_probability=float(row.get("prediction_probability", 0.0)),
                    ml_risk_score=float(row.get("ml_risk_score", 0.0)),
                    behavioral_risk_score=float(row.get("behavioral_risk_score", 0.0)),
                    final_risk_score=float(row.get("final_risk_score", 0.0)),
                    severity=str(row.get("severity", "Low"))
                )
                records.append(rec)
            db.bulk_save_objects(records)
            db.commit()
            print(f"Database: Loaded {len(records)} records from CSV.")
        else:
            print("Database: Seeding CERT r4.2 behavioral dataset records...")
            records = []
            base_date = datetime(2010, 1, 4)
            
            # Generate 1,000 CERT dataset users across 30 days
            user_ids = [f"USR{i:04d}" for i in range(1, 995)] + HIGH_RISK_USERS_LIST
            
            for u_idx, u in enumerate(user_ids):
                is_high_risk_user = u in HIGH_RISK_USERS_LIST
                for day_offset in range(30):
                    current_day = (base_date + timedelta(days=day_offset)).strftime("%Y-%m-%d")
                    
                    if is_high_risk_user and day_offset in [10, 15, 20, 25]:
                        # Suspicious day parameters
                        off_hours_logons = random.randint(3, 8)
                        device_connects = random.randint(4, 12)
                        sensitive_file_count = random.randint(10, 35)
                        external_email = random.randint(8, 25)
                        off_hours_http = random.randint(50, 200)
                        logon_count = random.randint(5, 10)
                        logoff_count = random.randint(4, 9)
                        unique_pcs = random.randint(2, 5)
                        attachment_count = random.randint(5, 15)
                    else:
                        # Normal day parameters
                        off_hours_logons = random.choice([0, 0, 0, 1])
                        device_connects = random.choice([0, 0, 1])
                        sensitive_file_count = random.choice([0, 1, 2])
                        external_email = random.choice([0, 1, 2, 3])
                        off_hours_http = random.choice([0, 0, 5, 10])
                        logon_count = random.choice([1, 2])
                        logoff_count = random.choice([1, 2])
                        unique_pcs = 1
                        attachment_count = random.choice([0, 1, 2])

                    feat = {
                        "logon_count": logon_count,
                        "logoff_count": logoff_count,
                        "off_hours_logons": off_hours_logons,
                        "unique_pcs": unique_pcs,
                        "device_connects": device_connects,
                        "device_disconnects": device_connects,
                        "unique_device_pcs": 1 if device_connects > 0 else 0,
                        "file_activity_count": sensitive_file_count + random.randint(1, 10),
                        "unique_file_pcs": 1,
                        "unique_files": sensitive_file_count + random.randint(1, 5),
                        "sensitive_file_count": sensitive_file_count,
                        "email_count": external_email + random.randint(5, 20),
                        "attachment_count": attachment_count,
                        "total_email_size": random.randint(10000, 250000),
                        "unique_email_pcs": 1,
                        "external_email_count": external_email,
                        "http_request_count": off_hours_http + random.randint(20, 150),
                        "unique_http_urls": random.randint(5, 40),
                        "off_hours_http": off_hours_http
                    }

                    res = predictor_service.predict(feat)

                    rec = BehavioralRiskRecord(
                        user=u,
                        day=current_day,
                        **feat,
                        prediction=res["prediction"],
                        prediction_probability=res["prediction_probability"],
                        ml_risk_score=res["ml_risk_score"],
                        behavioral_risk_score=res["behavioral_risk_score"],
                        final_risk_score=res["final_risk_score"],
                        severity=res["severity"]
                    )
                    records.append(rec)

            db.bulk_save_objects(records)
            db.commit()
            print(f"Database: Successfully seeded {len(records)} behavioral risk records.")

    # 3. Seed Security Alerts for High/Critical risk records
    if db.query(SecurityAlert).count() == 0:
        high_risk_recs = db.query(BehavioralRiskRecord).filter(
            BehavioralRiskRecord.severity.in_(["Critical", "High"])
        ).limit(25).all()

        for rec in high_risk_recs:
            alert = SecurityAlert(
                user=rec.user,
                day=rec.day,
                severity=rec.severity,
                risk_score=rec.final_risk_score,
                status="New" if rec.final_risk_score > 80 else "In Progress",
                title=f"Anomalous Insider Activity by {rec.user}",
                description=f"User {rec.user} on {rec.day} exhibited high risk (Score: {rec.final_risk_score}) with {rec.sensitive_file_count} sensitive file accesses, {rec.device_connects} USB connects, and {rec.off_hours_logons} after-hours logons."
            )
            db.add(alert)
        db.commit()
        print(f"Database: Created initial security alerts.")

    # 4. Seed Initial Investigations
    if db.query(Investigation).count() == 0:
        alerts = db.query(SecurityAlert).filter(SecurityAlert.severity == "Critical").limit(5).all()
        for alt in alerts:
            inv = Investigation(
                alert_id=alt.id,
                user=alt.user,
                assigned_analyst="analyst",
                status="Open" if alt.id % 2 == 0 else "In Progress",
                title=f"Investigation into {alt.user} - Exfiltration Risk",
                summary=f"Investigating suspicious USB device usage and external email exfiltration during off-hours on {alt.day}.",
                notes="Initial log analysis shows unauthorized access to customer files. Device connection verified.",
                risk_factors="After-hours Logon, Mass File Copy, External Email"
            )
            db.add(inv)
        db.commit()
        print("Database: Created initial investigation cases.")
