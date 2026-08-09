"""
CERT LDAP Seeding Script
========================
Onboards all employees from the CERT r4.2 LDAP registry.
Looks for data/cert/ldap.csv or files in data/cert/ldap/*.csv.
Usage: python scripts/seed_cert_employees.py
"""
import os
import sys
import glob
import pandas as pd
import random
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.database import SessionLocal, create_db_and_tables
from app.models import Department, Employee, Device

create_db_and_tables()
db = SessionLocal()

def get_ldap_filepath():
    # 1. Check for single file
    single_file = os.path.join("data", "cert", "ldap.csv")
    if os.path.exists(single_file):
        return single_file
        
    # 2. Check for directory of snapshots
    dir_path = os.path.join("data", "cert", "ldap")
    if os.path.exists(dir_path):
        csv_files = sorted(glob.glob(os.path.join(dir_path, "*.csv")))
        if csv_files:
            # We take the first snapshot (chronologically the earliest baseline)
            return csv_files[0]
            
    # 3. Check for any CSV files under data/cert matching ldap
    fallback_files = glob.glob(os.path.join("data", "cert", "*ldap*.csv"))
    if fallback_files:
        return fallback_files[0]
        
    return None

def seed_ldap_employees():
    filepath = get_ldap_filepath()
    if not filepath:
        print("❌ Error: Could not locate CERT LDAP file.")
        print("Please place your CERT LDAP file at:")
        print("   - data/cert/ldap.csv")
        print("   - OR data/cert/ldap/2009-12.csv (or similar snapshot)")
        return
        
    print(f"📖 Found CERT LDAP registry file: {filepath}")
    
    try:
        df = pd.read_csv(filepath)
    except Exception as e:
        print(f"❌ Error reading CSV file: {e}")
        return
        
    # Standardize column names
    df.columns = [col.strip().lower() for col in df.columns]
    
    # Required columns: employee_name/name, user_id/user/employee_id, email, role/designation, department/functional_unit/business_unit
    name_col = next((c for c in ['employee_name', 'name', 'full_name'] if c in df.columns), None)
    id_col = next((c for c in ['user_id', 'user', 'employee_id'] if c in df.columns), None)
    email_col = next((c for c in ['email', 'mail'] if c in df.columns), None)
    role_col = next((c for c in ['role', 'designation', 'title'] if c in df.columns), None)
    dept_col = next((c for c in ['department', 'functional_unit', 'business_unit', 'unit'] if c in df.columns), None)
    
    if not (name_col and id_col and email_col):
        print(f"❌ Error: CSV must contain name, user_id, and email columns. Found columns: {list(df.columns)}")
        return
        
    print(f"Processing {len(df)} employee records...")
    
    # 1. Cache existing departments
    db_depts = db.query(Department).all()
    depts_cache = {d.code.upper(): d for d in db_depts}
    
    # 2. Iterate and seed
    employees_onboarded = 0
    devices_registered = 0
    
    for idx, row in df.iterrows():
        emp_id = str(row[id_col]).strip()
        full_name = str(row[name_col]).strip()
        email = str(row[email_col]).strip()
        
        # Check if already exists
        existing_emp = db.query(Employee).filter(Employee.employee_id == emp_id).first()
        if existing_emp:
            continue
            
        role = str(row[role_col]).strip() if role_col else "Staff Member"
        dept_name = str(row[dept_col]).strip() if dept_col else "General"
        
        # Resolve department
        dept_code = dept_name[:10].upper().replace(" ", "_")
        if dept_code not in depts_cache:
            # Create new department
            new_dept = Department(
                name=dept_name,
                code=dept_code,
                description=f"Automated department mapping for {dept_name}"
            )
            db.add(new_dept)
            db.flush()
            depts_cache[dept_code] = new_dept
            print(f"🏢 Created department: {dept_name} ({dept_code})")
            
        dept = depts_cache[dept_code]
        
        # Create employee
        hire_year = random.choice([2020, 2021, 2022, 2023])
        new_emp = Employee(
            employee_id=emp_id,
            full_name=full_name,
            email=email,
            designation=role,
            department_id=dept.id,
            hire_date=datetime(hire_year, random.randint(1,12), random.randint(1,28), tzinfo=timezone.utc),
            access_level=random.choice(["standard", "elevated", "privileged"]) if role != "IT Admin" else "privileged",
            is_active=True,
            is_terminated=False
        )
        db.add(new_emp)
        db.flush()
        employees_onboarded += 1
        
        # Register a default workspace workstation/device for matching log ingestion
        dev_id = f"DEV-{emp_id}-001"
        existing_dev = db.query(Device).filter(Device.device_id == dev_id).first()
        if not existing_dev:
            new_dev = Device(
                employee_id=new_emp.id,
                device_name=f"PC-{emp_id}",
                device_type="workstation",
                device_id=dev_id,
                os="Windows 10",
                ip_address=f"192.168.{random.randint(1, 254)}.{random.randint(10, 250)}",
                mac_address=f"00:15:5D:{random.randint(0, 255):02X}:{random.randint(0, 255):02X}:{random.randint(0, 255):02X}",
                is_authorized=True
            )
            db.add(new_dev)
            devices_registered += 1
            
    db.commit()
    print("=========================================")
    print(f"✅ Onboarded CERT Employees: {employees_onboarded}")
    print(f"✅ Registered Devices:       {devices_registered}")
    print("=========================================")

if __name__ == "__main__":
    seed_ldap_employees()
    db.close()
