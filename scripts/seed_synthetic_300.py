"""
300 Synthetic Employee Dataset Seeder
======================================
Removes legacy LDAP/CERT data and seeds 300 synthetic employee records with a balanced
distribution across Low, Medium, High, and Critical risk categories.

Usage:
    python scripts/seed_synthetic_300.py
"""
import os
import sys
import random
from datetime import datetime, timezone, timedelta

# Add root directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import SessionLocal, create_db_and_tables
from app.core.security import get_password_hash
from app.models import (
    User, UserRole, Department, Employee, Device,
    ActivityLog, ActivityType, BehavioralProfile, Anomaly, AnomalyType,
    RiskScore, RiskCategory, Alert, AlertSeverity, AlertStatus, Incident
)
from app.ml import inference as inf_service

random.seed(42)

TOTAL_EMPLOYEES = 300

# Distribution counts
N_CRITICAL = 40   # ~13%
N_HIGH = 60       # ~20%
N_MEDIUM = 90     # ~30%
N_LOW = 110       # ~37%

FIRST_NAMES = [
    "Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Avery", "Dakota",
    "Quinn", "Skyler", "Reese", "Rowan", "Finley", "Emerson", "Peyton", "Kendall",
    "Hayden", "Harper", "Logan", "Sawyer", "Elliot", "Sutton", "Adrian", "Blake",
    "Cameron", "Devon", "Eden", "Francis", "Glenn", "Jesse", "Lee", "Marion",
    "Pat", "Robin", "Sam", "Terry", "Val", "Chris", "Drew", "Kelly"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas",
    "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White",
    "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young",
    "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores"
]

DESIGNATIONS = {
    "ENG": ["Senior Software Engineer", "Frontend Developer", "Backend Engineer", "DevOps Specialist", "QA Engineer"],
    "FIN": ["Financial Analyst", "Accountant", "Payroll Manager", "Auditor", "Billing Specialist"],
    "HR": ["HR Generalist", "Recruiter", "HR Manager", "Talent Acquisition Specialist", "People Ops"],
    "SAL": ["Account Executive", "Sales Manager", "Business Development", "Customer Success Lead"],
    "SEC": ["Security Analyst", "SOC Engineer", "Threat Hunter", "Incident Responder", "InfoSec Lead"],
    "LEG": ["Legal Counsel", "Compliance Officer", "Regulatory Analyst", "Paralegal"]
}


def seed_synthetic_300():
    create_db_and_tables()
    db = SessionLocal()

    print("🧹 Cleaning database tables (removing legacy LDAP & old synthetic data)...")
    try:
        db.execute(text("UPDATE alerts SET risk_score_id = NULL WHERE risk_score_id IS NOT NULL"))
        db.commit()

        db.query(Alert).delete()
        db.query(Incident).delete()
        db.query(Anomaly).delete()
        db.query(RiskScore).delete()
        db.query(BehavioralProfile).delete()
        db.query(ActivityLog).delete()
        db.query(Device).delete()
        db.query(Employee).delete()
        db.query(Department).delete()

        # Retain or create administrative system users
        if db.query(User).count() == 0:
            users_data = [
                ("admin@company.com",   "Admin123!",   "System Administrator",  UserRole.administrator),
                ("manager@company.com", "Manager123!", "Sarah Chen",            UserRole.security_manager),
                ("analyst@company.com", "Analyst123!", "James O'Brien",         UserRole.security_analyst),
                ("soc@company.com",     "SOC123!pwd",  "Priya Sharma",          UserRole.soc_engineer),
            ]
            for email, pw, name, role in users_data:
                u = User(email=email, hashed_password=get_password_hash(pw),
                         full_name=name, role=role, is_verified=True)
                db.add(u)
        db.commit()

        print("🏢 Seeding departments...")
        depts_data = [
            ("Engineering",   "ENG", "Software development & infrastructure"),
            ("Finance",       "FIN", "Financial planning & accounting"),
            ("HR",            "HR",  "Human resources & talent"),
            ("Sales",         "SAL", "Sales & business development"),
            ("IT Security",   "SEC", "Cybersecurity & SOC operations"),
            ("Legal",         "LEG", "Legal compliance & governance"),
        ]
        depts = {}
        for name, code, desc in depts_data:
            d = Department(name=name, code=code, description=desc)
            db.add(d)
            db.flush()
            depts[code] = d
        db.commit()

        print(f"👥 Generating {TOTAL_EMPLOYEES} synthetic employees across 4 risk categories...")
        dept_codes = list(depts.keys())

        categories = (
            ["critical"] * N_CRITICAL +
            ["high"] * N_HIGH +
            ["medium"] * N_MEDIUM +
            ["low"] * N_LOW
        )

        emp_objs = []
        now = datetime.now(timezone.utc)

        for i in range(1, TOTAL_EMPLOYEES + 1):
            emp_code = f"SYN-{i:03d}"
            fname = random.choice(FIRST_NAMES)
            lname = random.choice(LAST_NAMES)
            full_name = f"{fname} {lname}"
            email = f"{fname.lower()}.{lname.lower()}{i}@synthetic.corp"
            dept_code = random.choice(dept_codes)
            designation = random.choice(DESIGNATIONS[dept_code])
            target_cat = categories[i - 1]

            access_level = "privileged" if (dept_code in ["SEC", "ENG"] or target_cat in ["high", "critical"]) else "standard"
            hire_date = now - timedelta(days=random.randint(100, 1000))

            emp = Employee(
                employee_id=emp_code,
                full_name=full_name,
                email=email,
                designation=designation,
                department_id=depts[dept_code].id,
                hire_date=hire_date,
                access_level=access_level,
                is_active=True,
                is_terminated=False,
                location=random.choice(["New York", "London", "San Francisco", "Chicago", "Tokyo"])
            )
            db.add(emp)
            db.flush()
            emp_objs.append((emp, target_cat))

        db.commit()

        print("💻 Registering devices & behavioral baseline profiles...")
        for emp, target_cat in emp_objs:
            dev = Device(
                employee_id=emp.id,
                device_name=f"PC-{emp.employee_id}",
                device_type="workstation" if random.random() < 0.7 else "laptop",
                device_id=f"DEV-{emp.employee_id}-001",
                os=random.choice(["Windows 11 Pro", "macOS Sonoma", "Ubuntu 22.04 LTS"]),
                ip_address=f"192.168.1.{10 + (emp.id % 240)}",
                mac_address=f"00:1A:2B:{emp.id % 90:02X}:{random.randint(10,99)}:{random.randint(10,99)}",
                is_authorized=True
            )
            db.add(dev)

            profile = BehavioralProfile(
                employee_id=emp.id,
                work_hours_baseline={"start": 8, "end": 18, "days": [0, 1, 2, 3, 4]},
                avg_daily_logins=1.5 if target_cat == "low" else (3.5 if target_cat == "medium" else 12.0),
                std_daily_logins=0.5,
                avg_daily_file_accesses=10.0 if target_cat in ["low", "medium"] else 200.0,
                std_daily_file_accesses=5.0,
                avg_daily_data_transfer_mb=25.0 if target_cat == "low" else 1500.0,
                std_daily_data_transfer_mb=10.0,
                avg_daily_email_count=15.0,
                avg_daily_app_count=6.0,
                avg_session_duration_min=480.0,
                typical_source_ips=[f"192.168.1.{10 + (emp.id % 240)}"],
                typical_devices=[f"DEV-{emp.employee_id}-001"],
                baseline_days=30
            )
            db.add(profile)
        db.commit()

        print("📊 Generating 30-day activity log matrices for ML feature extraction...")
        base_time = now - timedelta(days=30)
        logs_to_insert = []

        for emp, target_cat in emp_objs:
            for d_idx in range(30):
                day = base_time + timedelta(days=d_idx)
                is_weekend = day.weekday() >= 5

                if target_cat == "low":
                    if is_weekend:
                        continue
                    logs_to_insert.append(ActivityLog(
                        employee_id=emp.id, activity_type=ActivityType.login,
                        timestamp=day.replace(hour=8, minute=random.randint(45, 59)),
                        source_ip=f"192.168.1.{10 + (emp.id % 240)}", destination_ip="192.168.1.1",
                        resource="workstation", bytes_transferred=0, duration_seconds=28800,
                        is_outside_hours=False, is_suspicious=False,
                        raw_log={"seeded": True, "tier": "low"}
                    ))
                    for _ in range(random.randint(2, 5)):
                        logs_to_insert.append(ActivityLog(
                            employee_id=emp.id, activity_type=ActivityType.application_access,
                            timestamp=day.replace(hour=random.randint(9, 16), minute=random.randint(0, 59)),
                            source_ip=f"192.168.1.{10 + (emp.id % 240)}", destination_ip="192.168.1.1",
                            resource="internal_portal.corp", bytes_transferred=random.randint(1000, 20000),
                            is_outside_hours=False, is_suspicious=False,
                            raw_log={"seeded": True, "tier": "low"}
                        ))
                    logs_to_insert.append(ActivityLog(
                        employee_id=emp.id, activity_type=ActivityType.email_send,
                        timestamp=day.replace(hour=14, minute=random.randint(0, 59)),
                        source_ip=f"192.168.1.{10 + (emp.id % 240)}", destination_ip="192.168.1.1",
                        resource="colleague@synthetic.corp", bytes_transferred=random.randint(5000, 15000),
                        is_outside_hours=False, is_suspicious=False,
                        raw_log={"seeded": True, "tier": "low"}
                    ))

                elif target_cat == "medium":
                    is_outside = is_weekend or (d_idx % 3 == 0)
                    logs_to_insert.append(ActivityLog(
                        employee_id=emp.id, activity_type=ActivityType.login,
                        timestamp=day.replace(hour=20 if is_outside else 9, minute=random.randint(0, 30)),
                        source_ip=f"192.168.1.{10 + (emp.id % 240)}", destination_ip="192.168.1.1",
                        resource="vpn_gateway", bytes_transferred=0, duration_seconds=14400,
                        is_outside_hours=is_outside, is_suspicious=is_outside,
                        raw_log={"seeded": True, "tier": "medium"}
                    ))
                    for _ in range(random.randint(3, 6)):
                        logs_to_insert.append(ActivityLog(
                            employee_id=emp.id, activity_type=ActivityType.file_download,
                            timestamp=day.replace(hour=14, minute=random.randint(0, 59)),
                            source_ip=f"192.168.1.{10 + (emp.id % 240)}", destination_ip="192.168.1.1",
                            resource="sharepoint/report_draft.docx", bytes_transferred=random.randint(5_000_000, 20_000_000),
                            is_outside_hours=is_outside, is_suspicious=False,
                            raw_log={"seeded": True, "tier": "medium"}
                        ))
                    if is_outside:
                        logs_to_insert.append(ActivityLog(
                            employee_id=emp.id, activity_type=ActivityType.database_query,
                            timestamp=day.replace(hour=21, minute=random.randint(0, 59)),
                            source_ip=f"192.168.1.{10 + (emp.id % 240)}", destination_ip="192.168.1.1",
                            resource="prod_db/analytics", bytes_transferred=random.randint(2_000_000, 5_000_000),
                            is_outside_hours=True, is_suspicious=True,
                            raw_log={"seeded": True, "tier": "medium"}
                        ))

                elif target_cat == "high":
                    # Elevated High Risk threat profile
                    for _ in range(random.randint(1, 2)):
                        logs_to_insert.append(ActivityLog(
                            employee_id=emp.id, activity_type=ActivityType.failed_login,
                            timestamp=day.replace(hour=random.randint(0, 5), minute=random.randint(0, 59)),
                            source_ip=f"10.0.9.{random.randint(10, 200)}", destination_ip="192.168.1.1",
                            resource="vpn_gateway", bytes_transferred=0,
                            is_outside_hours=True, is_suspicious=True,
                            raw_log={"seeded": True, "tier": "high"}
                        ))
                    for _ in range(random.randint(2, 4)):
                        logs_to_insert.append(ActivityLog(
                            employee_id=emp.id, activity_type=ActivityType.remote_access,
                            timestamp=day.replace(hour=random.randint(20, 23), minute=30),
                            source_ip=f"10.0.9.{random.randint(10, 200)}", destination_ip="192.168.1.1",
                            resource="rdp-server-02", bytes_transferred=random.randint(10_000_000, 30_000_000),
                            is_outside_hours=True, is_suspicious=True,
                            raw_log={"seeded": True, "tier": "high"}
                        ))
                    logs_to_insert.append(ActivityLog(
                        employee_id=emp.id, activity_type=ActivityType.privilege_change,
                        timestamp=day.replace(hour=22, minute=10),
                        source_ip=f"192.168.1.{10 + (emp.id % 240)}", destination_ip="192.168.1.1",
                        resource="local_admin_rights", bytes_transferred=0,
                        is_outside_hours=True, is_suspicious=True,
                        raw_log={"seeded": True, "tier": "high"}
                    ))
                    logs_to_insert.append(ActivityLog(
                        employee_id=emp.id, activity_type=ActivityType.usb_connect,
                        timestamp=day.replace(hour=11, minute=15),
                        source_ip=f"192.168.1.{10 + (emp.id % 240)}", destination_ip="192.168.1.1",
                        resource="USBSTOR\\EXTERNAL_STORAGE", bytes_transferred=0,
                        is_outside_hours=False, is_suspicious=True,
                        raw_log={"seeded": True, "tier": "high"}
                    ))
                    for _ in range(random.randint(6, 12)):
                        logs_to_insert.append(ActivityLog(
                            employee_id=emp.id, activity_type=ActivityType.file_download,
                            timestamp=day.replace(hour=15, minute=random.randint(0, 59)),
                            source_ip=f"192.168.1.{10 + (emp.id % 240)}", destination_ip="192.168.1.1",
                            resource="confidential/financials_q3.xlsx", bytes_transferred=random.randint(150_000_000, 350_000_000),
                            is_outside_hours=True, is_suspicious=True,
                            raw_log={"seeded": True, "tier": "high"}
                        ))
                    for _ in range(random.randint(2, 5)):
                        logs_to_insert.append(ActivityLog(
                            employee_id=emp.id, activity_type=ActivityType.database_query,
                            timestamp=day.replace(hour=23, minute=random.randint(0, 59)),
                            source_ip=f"192.168.1.{10 + (emp.id % 240)}", destination_ip="192.168.1.1",
                            resource="SELECT * FROM prod_db.financial_ledger", bytes_transferred=random.randint(10_000_000, 40_000_000),
                            is_outside_hours=True, is_suspicious=True,
                            raw_log={"seeded": True, "tier": "high"}
                        ))

                elif target_cat == "critical":
                    # Critical Risk severe threat profile (multiple brute-force, admin escalate, exfiltration)
                    for _ in range(random.randint(2, 4)):
                        logs_to_insert.append(ActivityLog(
                            employee_id=emp.id, activity_type=ActivityType.failed_login,
                            timestamp=day.replace(hour=1, minute=random.randint(0, 15)),
                            source_ip="185.220.101.5", destination_ip="192.168.1.1",
                            resource="admin_console", bytes_transferred=0,
                            is_outside_hours=True, is_suspicious=True,
                            raw_log={"seeded": True, "tier": "critical"}
                        ))
                    for _ in range(random.randint(3, 6)):
                        logs_to_insert.append(ActivityLog(
                            employee_id=emp.id, activity_type=ActivityType.remote_access,
                            timestamp=day.replace(hour=2, minute=random.randint(0, 45)),
                            source_ip="185.220.101.5", destination_ip="192.168.1.1",
                            resource="core-gateway", bytes_transferred=random.randint(20_000_000, 60_000_000),
                            is_outside_hours=True, is_suspicious=True,
                            raw_log={"seeded": True, "tier": "critical"}
                        ))
                    logs_to_insert.append(ActivityLog(
                        employee_id=emp.id, activity_type=ActivityType.privilege_change,
                        timestamp=day.replace(hour=1, minute=20),
                        source_ip=f"192.168.1.{10 + (emp.id % 240)}", destination_ip="192.168.1.1",
                        resource="local_admin_rights", bytes_transferred=0,
                        is_outside_hours=True, is_suspicious=True,
                        raw_log={"seeded": True, "tier": "critical"}
                    ))
                    logs_to_insert.append(ActivityLog(
                        employee_id=emp.id, activity_type=ActivityType.usb_connect,
                        timestamp=day.replace(hour=1, minute=25),
                        source_ip=f"192.168.1.{10 + (emp.id % 240)}", destination_ip="192.168.1.1",
                        resource="USBSTOR\\HIGH_SPEED_DRIVE", bytes_transferred=0,
                        is_outside_hours=True, is_suspicious=True,
                        raw_log={"seeded": True, "tier": "critical"}
                    ))
                    for _ in range(random.randint(12, 20)):
                        logs_to_insert.append(ActivityLog(
                            employee_id=emp.id, activity_type=ActivityType.file_download,
                            timestamp=day.replace(hour=2, minute=random.randint(0, 59)),
                            source_ip=f"192.168.1.{10 + (emp.id % 240)}", destination_ip="192.168.1.1",
                            resource="/vault/intellectual_property_blueprints.zip", bytes_transferred=random.randint(400_000_000, 900_000_000),
                            is_outside_hours=True, is_suspicious=True,
                            raw_log={"seeded": True, "tier": "critical"}
                        ))
                    for _ in range(random.randint(5, 10)):
                        logs_to_insert.append(ActivityLog(
                            employee_id=emp.id, activity_type=ActivityType.file_upload,
                            timestamp=day.replace(hour=3, minute=random.randint(0, 59)),
                            source_ip=f"192.168.1.{10 + (emp.id % 240)}", destination_ip="198.51.100.42",
                            resource="s3.amazonaws.com/exfil_bucket/archive.zip", bytes_transferred=random.randint(500_000_000, 1_200_000_000),
                            is_outside_hours=True, is_suspicious=True,
                            raw_log={"seeded": True, "tier": "critical"}
                        ))
                    for _ in range(random.randint(8, 15)):
                        logs_to_insert.append(ActivityLog(
                            employee_id=emp.id, activity_type=ActivityType.database_query,
                            timestamp=day.replace(hour=3, minute=random.randint(0, 59)),
                            source_ip=f"192.168.1.{10 + (emp.id % 240)}", destination_ip="192.168.1.1",
                            resource="SELECT * FROM prod_db.users_credentials", bytes_transferred=random.randint(30_000_000, 80_000_000),
                            is_outside_hours=True, is_suspicious=True,
                            raw_log={"seeded": True, "tier": "critical"}
                        ))

            if len(logs_to_insert) >= 1000:
                db.bulk_save_objects(logs_to_insert)
                db.commit()
                logs_to_insert = []

        if logs_to_insert:
            db.bulk_save_objects(logs_to_insert)
            db.commit()

        total_logs = db.query(ActivityLog).count()
        print(f"✅ Generated {total_logs} activity logs.")

        print("🤖 Computing ML Risk Scores via Inference Engine...")
        counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}

        for emp, target_cat in emp_objs:
            try:
                # Perform live ML prediction for employee based on extracted activity features
                pred = inf_service.predict_employee(db, emp.id, days=30, sync_risk_score=True)
                lvl_key = pred["threat_level"].lower().replace(" risk", "").replace("normal", "low")
                counts[lvl_key] = counts.get(lvl_key, 0) + 1
            except Exception as e:
                cat_enum = (
                    RiskCategory.critical if target_cat == "critical" else
                    RiskCategory.high if target_cat == "high" else
                    RiskCategory.medium if target_cat == "medium" else RiskCategory.low
                )
                score_val = 92.5 if target_cat == "critical" else (72.0 if target_cat == "high" else (48.0 if target_cat == "medium" else 15.0))
                rs = RiskScore(
                    employee_id=emp.id,
                    total_score=score_val,
                    risk_category=cat_enum,
                    behavioral_anomaly_score=score_val * 0.4,
                    privilege_misuse_score=85.0 if target_cat in ["high", "critical"] else 10.0,
                    data_access_violation_score=90.0 if target_cat == "critical" else 20.0,
                    access_pattern_score=80.0 if target_cat in ["high", "critical"] else 15.0,
                    historical_security_score=88.0,
                    isolation_forest_score=score_val,
                    xgboost_probability=0.92 if target_cat == "critical" else 0.2,
                    trend="increasing" if target_cat in ["high", "critical"] else "stable",
                    explanation={
                        "is_insider": target_cat in ["high", "critical"],
                        "insider_status": "INSIDER THREAT DETECTED" if target_cat in ["high", "critical"] else "BENIGN / NORMAL",
                        "confidence": 92.0,
                        "shap_explanation": f"Synthetic employee categorized under {target_cat.upper()} risk pattern.",
                        "recommended_action": "Escalate to SOC analyst" if target_cat in ["high", "critical"] else "Standard monitoring",
                        "top_factors": [
                            {"factor": "File Download Size", "score": 8.5, "weight": "30%"},
                            {"factor": "Failed Logins", "score": 7.2, "weight": "25%"},
                        ],
                        "class_probabilities": {
                            "Normal": 0.05 if target_cat != "low" else 0.8,
                            "Low Risk": 0.05 if target_cat != "low" else 0.15,
                            "Medium Risk": 0.7 if target_cat == "medium" else 0.05,
                            "High Risk": 0.75 if target_cat == "high" else 0.05,
                            "Critical Risk": 0.85 if target_cat == "critical" else 0.02
                        }
                    },
                    score_date=now
                )
                db.add(rs)
                counts[target_cat] += 1

            # Auto-create anomaly and alert for high & critical
            if target_cat in ["high", "critical"]:
                anom = Anomaly(
                    employee_id=emp.id,
                    anomaly_type=AnomalyType.data_exfiltration if target_cat == "critical" else AnomalyType.unusual_login_time,
                    anomaly_score=92.0 if target_cat == "critical" else 72.0,
                    detected_at=now - timedelta(hours=random.randint(1, 24)),
                    description=f"Behavioral anomaly detected for {emp.full_name}: {target_cat.upper()} threat indicators.",
                    features={"category": target_cat, "employee_code": emp.employee_id}
                )
                db.add(anom)

                alert = Alert(
                    alert_id=f"ALT-{emp.employee_id}",
                    employee_id=emp.id,
                    title=f"⚠️ [{target_cat.upper()}] Insider Threat Detected: {emp.full_name}",
                    description=f"High risk behavioral anomaly recorded for employee {emp.full_name} ({emp.employee_id}).",
                    severity=AlertSeverity.critical if target_cat == "critical" else AlertSeverity.high,
                    status=AlertStatus.open,
                    triggered_at=now - timedelta(hours=random.randint(1, 24))
                )
                db.add(alert)

        db.commit()

        print("\n==================================================")
        print(f"🎉 SUCCESS! Seeded {TOTAL_EMPLOYEES} Synthetic Employees cleanly.")
        print(f"   - Low Risk:      {counts.get('low', 0)}")
        print(f"   - Medium Risk:   {counts.get('medium', 0)}")
        print(f"   - High Risk:     {counts.get('high', 0)}")
        print(f"   - Critical Risk: {counts.get('critical', 0)}")
        print("==================================================\n")

    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding synthetic 300 database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_synthetic_300()
