"""
Seed script — creates demo users, departments, employees, and synthetic activity logs.
Run: python scripts/seed.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from datetime import datetime, timezone, timedelta
import random
from app.core.database import SessionLocal, create_db_and_tables
from app.core.security import get_password_hash
from app.models import (
    User, UserRole, Department, Employee, Device,
    ActivityLog, ActivityType, BehavioralProfile
)

create_db_and_tables()
db = SessionLocal()

print("Seeding database...")

# ── Users ─────────────────────────────────────────────────────────────────────
users_data = [
    ("admin@company.com",    "Admin123!",   "System Administrator",  UserRole.administrator),
    ("manager@company.com",  "Manager123!", "Sarah Chen",            UserRole.security_manager),
    ("analyst@company.com",  "Analyst123!", "James O'Brien",         UserRole.security_analyst),
    ("soc@company.com",      "SOC123!pwd",  "Priya Sharma",          UserRole.soc_engineer),
]
created_users = []
for email, pw, name, role in users_data:
    if not db.query(User).filter(User.email == email).first():
        u = User(email=email, hashed_password=get_password_hash(pw),
                 full_name=name, role=role, is_verified=True)
        db.add(u)
        created_users.append(u)
db.commit()
print(f"  Created {len(created_users)} users")

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
    d = db.query(Department).filter(Department.code == code).first()
    if not d:
        d = Department(name=name, code=code, description=desc)
        db.add(d); db.flush()
    depts[code] = d
db.commit()
print(f"  Created {len(depts)} departments")

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
    emp = db.query(Employee).filter(Employee.employee_id == emp_id).first()
    if not emp:
        emp = Employee(
            employee_id=emp_id, full_name=name, email=email,
            designation=designation, department_id=depts[dept_code].id,
            hire_date=datetime(2022, random.randint(1,12), random.randint(1,28),
                               tzinfo=timezone.utc),
            access_level=random.choice(["standard", "elevated", "privileged"]),
        )
        db.add(emp); db.flush()
    emp_objs.append(emp)
db.commit()
print(f"  Created {len(emp_objs)} employees")

# ── Devices ───────────────────────────────────────────────────────────────────
for i, emp in enumerate(emp_objs):
    dev = Device(
        employee_id=emp.id,
        device_name=f"LAPTOP-{emp.employee_id}",
        device_type="laptop",
        device_id=f"DEV-{emp.employee_id}-001",
        os=random.choice(["Windows 11", "macOS 14", "Ubuntu 22.04"]),
        ip_address=f"192.168.1.{10+i}",
        mac_address=f"AA:BB:CC:DD:EE:{i:02X}",
        is_authorized=True,
    )
    db.add(dev)
db.commit()

# ── Synthetic activity logs (90 days) ─────────────────────────────────────────
activity_types = list(ActivityType)
normal_hours = list(range(8, 18))
suspicious_emp_id = emp_objs[1].id  # Bob — will be risky

logs = []
base_time = datetime.now(timezone.utc) - timedelta(days=90)

for emp in emp_objs:
    for day_offset in range(90):
        day = base_time + timedelta(days=day_offset)
        n_events = random.randint(5, 25)
        for _ in range(n_events):
            is_suspicious_emp = emp.id == suspicious_emp_id
            # Suspicious employee logs more outside hours and does more data transfers
            if is_suspicious_emp and random.random() < 0.4:
                hour = random.choice([0, 1, 2, 22, 23])
            else:
                hour = random.choice(normal_hours)
            ts = day.replace(hour=hour, minute=random.randint(0,59))

            if is_suspicious_emp:
                act_type = random.choices(
                    [ActivityType.data_transfer, ActivityType.file_download,
                     ActivityType.usb_connect, ActivityType.login],
                    weights=[30, 30, 10, 30]
                )[0]
                bytes_transferred = random.randint(10_000_000, 500_000_000)  # 10MB–500MB
            else:
                act_type = random.choice(activity_types)
                bytes_transferred = random.randint(1_000, 5_000_000)

            is_outside = hour < 8 or hour >= 18 or ts.weekday() >= 5
            logs.append(ActivityLog(
                employee_id=emp.id,
                activity_type=act_type,
                timestamp=ts,
                source_ip=f"192.168.1.{random.randint(1,254)}",
                resource=f"/data/file_{random.randint(1,1000)}.dat" if "file" in act_type.value else None,
                bytes_transferred=bytes_transferred,
                is_outside_hours=is_outside,
                is_suspicious=is_outside and is_suspicious_emp,
            ))

        if len(logs) >= 500:
            db.bulk_save_objects(logs)
            db.commit()
            logs = []

if logs:
    db.bulk_save_objects(logs)
    db.commit()

total_logs = db.query(ActivityLog).count()
print(f"  Created {total_logs} activity logs")

db.close()
print("\nSeed complete!")
print("\nLogin credentials:")
for email, pw, name, role in users_data:
    print(f"  {role.value:25s}  {email:35s}  {pw}")
print("\nStart API: uvicorn app.main:app --reload")
print("Docs:      http://localhost:8000/docs")
