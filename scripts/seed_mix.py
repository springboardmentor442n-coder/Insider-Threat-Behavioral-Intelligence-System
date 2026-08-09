import sys
import os
from datetime import datetime, timezone, timedelta
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import func
from app.core.database import SessionLocal, create_db_and_tables
from app.core.security import get_password_hash
from app.models import (
    User, UserRole, Department, Employee, Device,
    ActivityLog, ActivityType, BehavioralProfile, Anomaly, RiskScore, Alert, Incident
)

create_db_and_tables()
db = SessionLocal()

print("Clearing old data from database...")
db.query(Alert).delete()
db.query(Incident).delete()
db.query(Anomaly).delete()
db.query(RiskScore).delete()
db.query(BehavioralProfile).delete()
db.query(ActivityLog).delete()
db.query(Device).delete()
db.query(Employee).delete()
db.query(Department).delete()
db.query(User).delete()
db.commit()

print("Seeding database with targeted scenario profiles...")

# ── Users ─────────────────────────────────────────────────────────────────────
users_data = [
    ("admin@company.com",    "Admin123!",   "System Administrator",  UserRole.administrator),
    ("manager@company.com",  "Manager123!", "Sarah Chen",            UserRole.security_manager),
    ("analyst@company.com",  "Analyst123!", "James O'Brien",         UserRole.security_analyst),
    ("soc@company.com",      "SOC123!pwd",  "Priya Sharma",          UserRole.soc_engineer),
]
for email, pw, name, role in users_data:
    u = User(email=email, hashed_password=get_password_hash(pw),
             full_name=name, role=role, is_verified=True)
    db.add(u)
db.commit()

# ── Departments ───────────────────────────────────────────────────────────────
depts_data = [
    ("Engineering",   "ENG", "Software & infrastructure"),
    ("Finance",       "FIN", "Financial operations"),
    ("HR",            "HR",  "Human resources"),
    ("Sales",         "SAL", "Sales & partnerships"),
    ("IT Security",   "SEC", "Cybersecurity operations"),
    ("Legal",         "LEG", "Legal & compliance"),
]
depts = {}
for name, code, desc in depts_data:
    d = Department(name=name, code=code, description=desc)
    db.add(d)
    db.flush()
    depts[code] = d
db.commit()

# ── Employees ─────────────────────────────────────────────────────────────────
EMPLOYEES = [
    ("EMP001", "Alice Johnson",  "alice@company.com",   "Senior Engineer",     "ENG"),
    ("EMP002", "Bob Martinez",   "bob@company.com",     "Finance Analyst",     "FIN"),
    ("EMP003", "Carol White",    "carol@company.com",   "HR Manager",          "HR"),
    ("EMP004", "David Lee",      "david@company.com",   "Sales Director",      "SAL"),
    ("EMP005", "Eva Brown",      "eva@company.com",     "Security Analyst",    "SEC"),
    ("EMP006", "Frank Wilson",   "frank@company.com",   "Legal Counsel",       "LEG"),
    ("EMP007", "Grace Kim",      "grace@company.com",   "DevOps Engineer",     "ENG"),
    ("EMP008", "Henry Davis",    "henry@company.com",   "Account Manager",     "SAL"),
    ("EMP009", "Iris Patel",     "iris@company.com",    "Payroll Specialist",  "FIN"),
    ("EMP010", "Jack Thompson",  "jack@company.com",    "IT Administrator",    "SEC"),
]
emp_objs = []
for emp_id, name, email, designation, dept_code in EMPLOYEES:
    emp = Employee(
        employee_id=emp_id, full_name=name, email=email,
        designation=designation, department_id=depts[dept_code].id,
        hire_date=datetime(2022, 6, 15, tzinfo=timezone.utc),
        access_level="privileged" if dept_code in ["SEC", "ENG"] else "standard",
    )
    db.add(emp)
    db.flush()
    emp_objs.append(emp)
db.commit()

# ── Devices ───────────────────────────────────────────────────────────────────
for i, emp in enumerate(emp_objs):
    dev = Device(
        employee_id=emp.id,
        device_name=f"LAPTOP-{emp.employee_id}",
        device_type="laptop",
        device_id=f"DEV-{emp.employee_id}-001",
        os="Windows 11",
        ip_address=f"192.168.1.{10+i}",
        mac_address=f"AA:BB:CC:DD:EE:{i:02X}",
        is_authorized=True,
    )
    db.add(dev)
db.commit()

# ── Pre-populate Behavioral Profiles ──────────────────────────────────────────
# This is crucial so that the baseline deviation features don't get divide-by-zero or default to 0.
for emp in emp_objs:
    profile = BehavioralProfile(
        employee_id=emp.id,
        work_hours_baseline={"start": 9, "end": 17, "days": [0, 1, 2, 3, 4]},
        avg_daily_logins=2.0,
        std_daily_logins=0.5,
        avg_daily_file_accesses=10.0,
        std_daily_file_accesses=2.0,
        avg_daily_data_transfer_mb=25.0,
        std_daily_data_transfer_mb=5.0,
        avg_daily_email_count=5.0,
        avg_daily_app_count=8.0,
        avg_session_duration_min=480.0,
        typical_source_ips=[f"192.168.1.{10+emp.id}"],
        typical_devices=[f"DEV-{emp.employee_id}-001"],
        baseline_days=30
    )
    db.add(profile)
db.commit()

# ── Generate Synthetic Logs (90 Days) ─────────────────────────────────────────
print("Generating logs (90 days matrix)...")
base_time = datetime.now(timezone.utc) - timedelta(days=90)
logs = []

for emp in emp_objs:
    # Check threat scenarios
    # EMP001 (Alice) -> Intellectual Property Theft (High file downloads, high night/off-hours activity)
    # EMP002 (Bob) -> IT Sabotage (High deletes, high privilege changes, off-hours)
    # EMP003 (Carol) -> Unauthorized Access (High login count, high off-hours login ratio, unique source IPs)
    # EMP004 (David) -> Data Exfiltration (High USB connect count, high data exfil indicators, external emails)
    # Others -> Normal

    for day_offset in range(90):
        day = base_time + timedelta(days=day_offset)
        is_weekend = day.weekday() >= 5

        # Normal employees don't work much on weekends, and work 9-5 on weekdays
        if emp.employee_id not in ["EMP001", "EMP002", "EMP003", "EMP004"]:
            if is_weekend:
                continue
            # Seed standard normal logs
            # Login
            logs.append(ActivityLog(
                employee_id=emp.id, activity_type=ActivityType.login,
                timestamp=day.replace(hour=9, minute=random.randint(0, 15)),
                source_ip=f"192.168.1.{10+emp.id}", is_outside_hours=False, is_suspicious=False
            ))
            # Normal HTTP/App access
            for _ in range(random.randint(5, 12)):
                logs.append(ActivityLog(
                    employee_id=emp.id, activity_type=ActivityType.application_access,
                    timestamp=day.replace(hour=random.randint(10, 16), minute=random.randint(0, 59)),
                    source_ip=f"192.168.1.{10+emp.id}", is_outside_hours=False, is_suspicious=False
                ))
            # Email send
            logs.append(ActivityLog(
                employee_id=emp.id, activity_type=ActivityType.email_send,
                timestamp=day.replace(hour=14, minute=random.randint(0, 45)),
                source_ip=f"192.168.1.{10+emp.id}", resource="colleague@company.com",
                bytes_transferred=random.randint(10_000, 50_000), is_outside_hours=False, is_suspicious=False
            ))
            # Logout
            logs.append(ActivityLog(
                employee_id=emp.id, activity_type=ActivityType.logout,
                timestamp=day.replace(hour=17, minute=random.randint(0, 15)),
                source_ip=f"192.168.1.{10+emp.id}", is_outside_hours=False, is_suspicious=False
            ))
            continue

        # Threat scenarios (inject normal behavior first, then malicious scenario spikes)
        # Normal behavior during most days, scenario peaks in the last 14 days
        in_scenario_window = day_offset >= 75

        if emp.employee_id == "EMP001":
            # ALICE: IP Theft
            if is_weekend and not in_scenario_window:
                continue
            
            # Normal day logic or scenario day logic
            if in_scenario_window:
                # Alice works at night (off-hours login and high night_activity_ratio)
                logs.append(ActivityLog(
                    employee_id=emp.id, activity_type=ActivityType.login,
                    timestamp=day.replace(hour=1, minute=random.randint(10, 30)),
                    source_ip=f"192.168.1.{10+emp.id}", is_outside_hours=True, is_suspicious=True
                ))
                # Downloads huge files (file_download_count and total_data_transfer_mb)
                for _ in range(12):
                    logs.append(ActivityLog(
                        employee_id=emp.id, activity_type=ActivityType.file_download,
                        timestamp=day.replace(hour=2, minute=random.randint(0, 59)),
                        source_ip=f"192.168.1.{10+emp.id}", resource="/vault/ip_blueprint.zip",
                        bytes_transferred=random.randint(50_000_000, 150_000_000), # 50-150MB
                        is_outside_hours=True, is_suspicious=True
                    ))
                # Uploads or transfers data
                logs.append(ActivityLog(
                    employee_id=emp.id, activity_type=ActivityType.file_upload,
                    timestamp=day.replace(hour=3, minute=30),
                    source_ip=f"192.168.1.{10+emp.id}", resource="/vault/external_repo",
                    bytes_transferred=random.randint(50_000_000, 200_000_000),
                    is_outside_hours=True, is_suspicious=True
                ))
                logs.append(ActivityLog(
                    employee_id=emp.id, activity_type=ActivityType.logout,
                    timestamp=day.replace(hour=4, minute=0),
                    source_ip=f"192.168.1.{10+emp.id}", is_outside_hours=True, is_suspicious=True
                ))
            else:
                # Regular Alice behavior
                logs.append(ActivityLog(
                    employee_id=emp.id, activity_type=ActivityType.login,
                    timestamp=day.replace(hour=9, minute=random.randint(0, 15)),
                    source_ip=f"192.168.1.{10+emp.id}", is_outside_hours=False, is_suspicious=False
                ))
                logs.append(ActivityLog(
                    employee_id=emp.id, activity_type=ActivityType.logout,
                    timestamp=day.replace(hour=17, minute=random.randint(0, 15)),
                    source_ip=f"192.168.1.{10+emp.id}", is_outside_hours=False, is_suspicious=False
                ))

        elif emp.employee_id == "EMP002":
            # BOB: IT Sabotage
            if is_weekend and not in_scenario_window:
                continue

            if in_scenario_window:
                # Bob logs in off hours
                logs.append(ActivityLog(
                    employee_id=emp.id, activity_type=ActivityType.login,
                    timestamp=day.replace(hour=23, minute=random.randint(0, 15)),
                    source_ip=f"192.168.1.{10+emp.id}", is_outside_hours=True, is_suspicious=True
                ))
                # Bob escalates privileges and deletes many key system files
                for _ in range(3):
                    logs.append(ActivityLog(
                        employee_id=emp.id, activity_type=ActivityType.privilege_change,
                        timestamp=day.replace(hour=23, minute=random.randint(16, 25)),
                        source_ip=f"192.168.1.{10+emp.id}", resource="system_root/admin_grant",
                        is_outside_hours=True, is_suspicious=True
                    ))
                for file_idx in range(15):
                    logs.append(ActivityLog(
                        employee_id=emp.id, activity_type=ActivityType.file_delete,
                        timestamp=day.replace(hour=23, minute=random.randint(30, 55)),
                        source_ip=f"192.168.1.{10+emp.id}", resource=f"db_prod/table_{file_idx}.sql",
                        is_outside_hours=True, is_suspicious=True
                    ))
                logs.append(ActivityLog(
                    employee_id=emp.id, activity_type=ActivityType.logout,
                    timestamp=day.replace(hour=23, minute=58),
                    source_ip=f"192.168.1.{10+emp.id}", is_outside_hours=True, is_suspicious=True
                ))
            else:
                logs.append(ActivityLog(
                    employee_id=emp.id, activity_type=ActivityType.login,
                    timestamp=day.replace(hour=9, minute=random.randint(0, 15)),
                    source_ip=f"192.168.1.{10+emp.id}", is_outside_hours=False, is_suspicious=False
                ))
                logs.append(ActivityLog(
                    employee_id=emp.id, activity_type=ActivityType.logout,
                    timestamp=day.replace(hour=17, minute=random.randint(0, 15)),
                    source_ip=f"192.168.1.{10+emp.id}", is_outside_hours=False, is_suspicious=False
                ))

        elif emp.employee_id == "EMP003":
            # CAROL: Unauthorized Access
            if in_scenario_window:
                # Carol logs in from a different IP address every day, and does it late at night
                for _ip in range(5):
                    logs.append(ActivityLog(
                        employee_id=emp.id, activity_type=ActivityType.login,
                        timestamp=day.replace(hour=random.randint(0, 5), minute=random.randint(0, 59)),
                        source_ip=f"10.0.9.{random.randint(10, 250)}", is_outside_hours=True, is_suspicious=True
                    ))
                for _ in range(25):
                    logs.append(ActivityLog(
                        employee_id=emp.id, activity_type=ActivityType.application_access,
                        timestamp=day.replace(hour=random.randint(2, 6), minute=random.randint(0, 59)),
                        source_ip=f"10.0.9.{random.randint(10, 250)}", resource="salary_sheet/hr_records",
                        is_outside_hours=True, is_suspicious=True
                    ))
            else:
                if is_weekend:
                    continue
                logs.append(ActivityLog(
                    employee_id=emp.id, activity_type=ActivityType.login,
                    timestamp=day.replace(hour=9, minute=random.randint(0, 15)),
                    source_ip=f"192.168.1.{10+emp.id}", is_outside_hours=False, is_suspicious=False
                ))
                logs.append(ActivityLog(
                    employee_id=emp.id, activity_type=ActivityType.logout,
                    timestamp=day.replace(hour=17, minute=random.randint(0, 15)),
                    source_ip=f"192.168.1.{10+emp.id}", is_outside_hours=False, is_suspicious=False
                ))

        elif emp.employee_id == "EMP004":
            # DAVID: Data Exfiltration
            if is_weekend and not in_scenario_window:
                continue

            if in_scenario_window:
                logs.append(ActivityLog(
                    employee_id=emp.id, activity_type=ActivityType.login,
                    timestamp=day.replace(hour=9, minute=random.randint(0, 15)),
                    source_ip=f"192.168.1.{10+emp.id}", is_outside_hours=False, is_suspicious=False
                ))
                # David connects USB keys (unauthorized_device_ratio and usb_connect_count)
                for _ in range(5):
                    logs.append(ActivityLog(
                        employee_id=emp.id, activity_type=ActivityType.usb_connect,
                        timestamp=day.replace(hour=10, minute=random.randint(0, 59)),
                        source_ip=f"192.168.1.{10+emp.id}", resource="USB-ST-RAND-32G",
                        is_outside_hours=False, is_suspicious=True
                    ))
                # David transfers data to USB (data_exfil_indicator -> large transfers outside hours or files)
                logs.append(ActivityLog(
                    employee_id=emp.id, activity_type=ActivityType.data_transfer,
                    timestamp=day.replace(hour=21, minute=30), # outside hours
                    source_ip=f"192.168.1.{10+emp.id}", resource="/local/export_customer_data.csv",
                    bytes_transferred=25_000_000, # 25MB (> 5MB)
                    is_outside_hours=True, is_suspicious=True
                ))
                # David sends external email with large attachment (external_email_ratio)
                logs.append(ActivityLog(
                    employee_id=emp.id, activity_type=ActivityType.email_send,
                    timestamp=day.replace(hour=16, minute=random.randint(0, 59)),
                    source_ip=f"192.168.1.{10+emp.id}", resource="competitor_scout@external.org",
                    bytes_transferred=50_000_000, # 50MB
                    is_outside_hours=False, is_suspicious=True
                ))
                logs.append(ActivityLog(
                    employee_id=emp.id, activity_type=ActivityType.logout,
                    timestamp=day.replace(hour=18, minute=15),
                    source_ip=f"192.168.1.{10+emp.id}", is_outside_hours=True, is_suspicious=False
                ))
            else:
                logs.append(ActivityLog(
                    employee_id=emp.id, activity_type=ActivityType.login,
                    timestamp=day.replace(hour=9, minute=random.randint(0, 15)),
                    source_ip=f"192.168.1.{10+emp.id}", is_outside_hours=False, is_suspicious=False
                ))
                logs.append(ActivityLog(
                    employee_id=emp.id, activity_type=ActivityType.logout,
                    timestamp=day.replace(hour=17, minute=random.randint(0, 15)),
                    source_ip=f"192.168.1.{10+emp.id}", is_outside_hours=False, is_suspicious=False
                ))

        if len(logs) >= 500:
            db.bulk_save_objects(logs)
            db.commit()
            logs = []

if logs:
    db.bulk_save_objects(logs)
    db.commit()

print(f"Ingested {db.query(ActivityLog).count()} activity logs successfully.")

from app.services import ml_service
ml_service.run_daily_scoring(db)

print("Scoring complete. Checking generated RiskScores and Alerts...")
# Count risk scores
rs_counts = db.query(RiskScore.risk_category, func.count(RiskScore.id)).group_by(RiskScore.risk_category).all()
print("Risk Scores Category counts:")
for cat, count in rs_counts:
    print(f"  {cat}: {count}")

# Check employee threat classes predictions
print("\nEmployee ML Predictions check:")
for emp in emp_objs:
    latest_score = db.query(RiskScore).filter(RiskScore.employee_id == emp.id).order_by(RiskScore.score_date.desc()).first()
    if latest_score:
        print(f"  {emp.employee_id} ({emp.full_name}): Category: {latest_score.risk_category}, Total Score: {latest_score.total_score:.2f}, Explanation: {latest_score.explanation}")

db.close()
print("\nDone seeding mix!")
