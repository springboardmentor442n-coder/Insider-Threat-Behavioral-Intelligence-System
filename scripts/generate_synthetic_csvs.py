"""
Synthetic CSV Generator (50 Rows)
==================================
Generates a synthetic dataset CSV with exactly 50 rows using the exact 20 ML feature
columns that the predict_csv endpoint expects. No label, expected, or score columns.

Feature columns (20 exactly):
  login_time, failed_logins, vpn_usage, usb_usage, file_downloads, file_uploads,
  email_count, cloud_uploads, device_changes, working_hours, privilege_escalation,
  database_access, website_visits, external_storage_usage, location, department,
  employee_role, session_duration, login_frequency, data_transfer_size

Distribution: 18 Low, 15 Medium, 10 High, 7 Critical
"""
import os
import csv
import random

# Exact canonical feature names used by FEATURE_NAMES in feature_engineering.py
FEATURE_NAMES = [
    "login_time",
    "failed_logins",
    "vpn_usage",
    "usb_usage",
    "file_downloads",
    "file_uploads",
    "email_count",
    "cloud_uploads",
    "device_changes",
    "working_hours",
    "privilege_escalation",
    "database_access",
    "website_visits",
    "external_storage_usage",
    "location",
    "department",
    "employee_role",
    "session_duration",
    "login_frequency",
    "data_transfer_size",
]

HEADERS = ["employee_code", "full_name", "department_name"] + FEATURE_NAMES


def generate_csvs():
    output_dir = os.path.join("data", "synthetic_csvs")
    os.makedirs(output_dir, exist_ok=True)
    random.seed(42)

    features_csv = os.path.join(output_dir, "synthetic_features_50.csv")

    # 50 rows: 18 Low, 15 Medium, 10 High, 7 Critical
    tiers = (
        ["Low Risk"] * 18 +
        ["Medium Risk"] * 15 +
        ["High Risk"] * 10 +
        ["Critical Risk"] * 7
    )
    random.shuffle(tiers)

    dept_names = ["Engineering", "Finance", "HR", "Sales", "IT Security", "Legal"]

    rows = []
    for i, tier in enumerate(tiers, 1):
        emp_code = f"SYN-{i:03d}"
        full_name = f"Employee {i:02d}"
        dept_name = random.choice(dept_names)

        if tier == "Low Risk":
            # Normal working hours, minimal suspicious activity
            features = {
                "login_time": round(random.uniform(8.0, 10.0), 1),
                "failed_logins": random.randint(0, 1),
                "vpn_usage": random.randint(0, 5),
                "usb_usage": 0,
                "file_downloads": random.randint(5, 20),
                "file_uploads": random.randint(2, 8),
                "email_count": random.randint(30, 150),
                "cloud_uploads": random.randint(0, 2),
                "device_changes": 1,
                "working_hours": round(random.uniform(0.01, 0.06), 3),
                "privilege_escalation": 0,
                "database_access": random.randint(1, 8),
                "website_visits": random.randint(80, 300),
                "external_storage_usage": 0,
                "location": random.choice([1, 2, 3]),
                "department": random.choice([1, 2, 3]),
                "employee_role": random.choice([1, 2]),
                "session_duration": random.randint(200, 500),
                "login_frequency": round(random.uniform(0.8, 1.5), 2),
                "data_transfer_size": random.randint(5, 80),
            }

        elif tier == "Medium Risk":
            # Some suspicious patterns — off-hours activity, elevated downloads
            features = {
                "login_time": round(random.uniform(17.0, 22.0), 1),
                "failed_logins": random.randint(3, 8),
                "vpn_usage": random.randint(20, 50),
                "usb_usage": random.randint(1, 4),
                "file_downloads": random.randint(80, 160),
                "file_uploads": random.randint(25, 70),
                "email_count": random.randint(250, 600),
                "cloud_uploads": random.randint(8, 30),
                "device_changes": random.randint(2, 4),
                "working_hours": round(random.uniform(0.25, 0.45), 3),
                "privilege_escalation": random.choice([0, 1]),
                "database_access": random.randint(25, 80),
                "website_visits": random.randint(450, 900),
                "external_storage_usage": random.randint(1, 4),
                "location": random.choice([2, 3, 4]),
                "department": random.choice([2, 3, 4]),
                "employee_role": random.choice([2, 3]),
                "session_duration": random.randint(700, 1600),
                "login_frequency": round(random.uniform(2.5, 4.5), 2),
                "data_transfer_size": random.randint(400, 2000),
            }

        elif tier == "High Risk":
            # Clear threat indicators — repeated failures, night logins, large data moves
            features = {
                "login_time": round(random.uniform(0.5, 5.0), 1),
                "failed_logins": random.randint(12, 22),
                "vpn_usage": random.randint(60, 130),
                "usb_usage": random.randint(5, 14),
                "file_downloads": random.randint(200, 380),
                "file_uploads": random.randint(100, 230),
                "email_count": random.randint(800, 1500),
                "cloud_uploads": random.randint(40, 100),
                "device_changes": random.randint(4, 8),
                "working_hours": round(random.uniform(0.5, 0.75), 3),
                "privilege_escalation": random.randint(2, 5),
                "database_access": random.randint(100, 280),
                "website_visits": random.randint(1000, 1800),
                "external_storage_usage": random.randint(6, 14),
                "location": random.choice([3, 4, 5]),
                "department": random.choice([4, 5]),
                "employee_role": random.choice([4, 5]),
                "session_duration": random.randint(2000, 4500),
                "login_frequency": round(random.uniform(5.0, 8.0), 2),
                "data_transfer_size": random.randint(3500, 8000),
            }

        else:  # Critical Risk
            # Extreme threat indicators — all high-risk signals elevated simultaneously
            features = {
                "login_time": round(random.uniform(1.0, 3.5), 1),
                "failed_logins": random.randint(28, 55),
                "vpn_usage": random.randint(140, 220),
                "usb_usage": random.randint(18, 35),
                "file_downloads": random.randint(480, 700),
                "file_uploads": random.randint(320, 600),
                "email_count": random.randint(1600, 2800),
                "cloud_uploads": random.randint(130, 220),
                "device_changes": random.randint(9, 16),
                "working_hours": round(random.uniform(0.80, 0.97), 3),
                "privilege_escalation": random.randint(6, 18),
                "database_access": random.randint(320, 650),
                "website_visits": random.randint(1800, 3200),
                "external_storage_usage": random.randint(18, 35),
                "location": random.choice([4, 5, 6, 7]),
                "department": random.choice([5, 6]),
                "employee_role": random.choice([7, 8]),
                "session_duration": random.randint(5500, 10000),
                "login_frequency": round(random.uniform(8.5, 12.0), 2),
                "data_transfer_size": random.randint(9000, 20000),
            }

        row = {
            "employee_code": emp_code,
            "full_name": full_name,
            "department_name": dept_name,
        }
        row.update(features)
        rows.append(row)

    with open(features_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"✅ Generated {len(rows)}-row synthetic features CSV at: {features_csv}")
    print(f"   Columns: {', '.join(HEADERS)}")
    print(f"   No expected_risk_category or score columns — 100% ML-predicted.")


if __name__ == "__main__":
    generate_csvs()
