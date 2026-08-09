"""
Feature Engineering for Insider Threat Detection
===============================================
Extracts exactly 20 behavioral features per employee, matching the specifications
required by the Isolation Forest and XGBoost hybrid risk scoring engine.
"""
import numpy as np
import pandas as pd
from datetime import datetime, timezone, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import ActivityLog, ActivityType, Employee, BehavioralProfile

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
    "data_transfer_size"
]

N_FEATURES = len(FEATURE_NAMES)
assert N_FEATURES == 20, f"Feature count mismatch: {N_FEATURES}"


def encode_location(loc_str: Optional[str]) -> float:
    if not loc_str:
        return 0.0
    loc_map = {
        "new york": 1.0,
        "london": 2.0,
        "san francisco": 3.0,
        "chicago": 4.0,
        "tokyo": 5.0,
        "paris": 6.0,
        "sydney": 7.0
    }
    return loc_map.get(loc_str.lower().strip(), 0.0)


def encode_department(dept_code: Optional[str]) -> float:
    if not dept_code:
        return 0.0
    dept_map = {
        "eng": 1.0,
        "fin": 2.0,
        "hr": 3.0,
        "sal": 4.0,
        "sec": 5.0,
        "leg": 6.0
    }
    return dept_map.get(dept_code.lower().strip(), 0.0)


def encode_role(role_str: Optional[str]) -> float:
    if not role_str:
        return 0.0
    r = role_str.lower()
    if "senior" in r:
        return 1.0
    elif "analyst" in r:
        return 2.0
    elif "manager" in r:
        return 3.0
    elif "director" in r:
        return 4.0
    elif "engineer" in r:
        return 5.0
    elif "counsel" in r:
        return 6.0
    elif "specialist" in r:
        return 7.0
    elif "admin" in r:
        return 8.0
    return 0.0


def extract_features(
    db: Session,
    employee_id: int,
    days: int = 30,
    reference_time: Optional[datetime] = None,
) -> np.ndarray:
    """
    Extract all 20 features for one employee over `days` window.
    Returns shape (20,) numpy array ready for StandardScaler.
    """
    if reference_time is None:
        latest_log = (
            db.query(func.max(ActivityLog.timestamp))
            .filter(ActivityLog.employee_id == employee_id)
            .scalar()
        )
        now = latest_log or datetime.now(timezone.utc)
    else:
        now = reference_time

    since = now - timedelta(days=days)

    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp:
        return np.zeros(N_FEATURES, dtype=np.float32)

    logs = (
        db.query(ActivityLog)
        .filter(
            ActivityLog.employee_id == employee_id,
            ActivityLog.timestamp >= since,
        )
        .all()
    )

    # Encode employee attributes
    dept_code = emp.department.code if emp.department else ""
    val_location = encode_location(emp.location)
    val_department = encode_department(dept_code)
    val_role = encode_role(emp.designation)

    if not logs:
        # Return default features filled with categorical and baseline zeros
        features = np.zeros(N_FEATURES, dtype=np.float32)
        features[14] = val_location
        features[15] = val_department
        features[16] = val_role
        return features

    # Process activities
    rows = []
    for log in logs:
        rows.append({
            "activity_type": log.activity_type.value,
            "timestamp": log.timestamp,
            "hour": log.timestamp.hour,
            "bytes": log.bytes_transferred or 0,
            "is_outside_hours": int(log.is_outside_hours),
            "is_suspicious": int(log.is_suspicious),
            "resource": log.resource or "",
            "duration": log.duration_seconds or 0,
            "device": log.device_id or 0
        })
    df = pd.DataFrame(rows)

    total_activities = len(df)

    # 1. Login Time (average login hour)
    logins = df[df["activity_type"] == "login"]
    login_time = float(logins["hour"].mean()) if not logins.empty else 9.0

    # 2. Failed Logins (suspicious logins or failed login activity logs)
    failed_logins = float(df[
        (df["activity_type"] == "failed_login") | 
        ((df["activity_type"] == "login") & (df["is_suspicious"] == 1))
    ].shape[0])

    # 3. VPN Usage (remote logins)
    vpn_usage = float(df[df["activity_type"] == "remote_access"].shape[0])

    # 4. USB Usage
    usb_usage = float(df[df["activity_type"] == "usb_connect"].shape[0])

    # 5. File Downloads
    file_downloads = float(df[df["activity_type"] == "file_download"].shape[0])

    # 6. File Uploads
    file_uploads = float(df[df["activity_type"] == "file_upload"].shape[0])

    # 7. Email Count
    email_count = float(df[df["activity_type"].isin(["email_send", "email_receive"])].shape[0])

    # 8. Cloud Uploads (Uploads to cloud resources)
    cloud_resources = ["drive.google.com", "dropbox.com", "s3.amazonaws.com", "onedrive.live.com", "box.com", "cloud"]
    cloud_filter = df["resource"].str.lower().str.contains("|".join(cloud_resources), na=False)
    cloud_uploads = float(df[(df["activity_type"] == "file_upload") & cloud_filter].shape[0])

    # 9. Device Changes (Unique device connect / usage changes)
    device_changes = float(df["device"].nunique())

    # 10. Working Hours (Ratio of activities done outside regular business hours)
    working_hours = float(df["is_outside_hours"].mean()) if total_activities > 0 else 0.0

    # 11. Privilege Escalation
    privilege_escalation = float(df[df["activity_type"] == "privilege_change"].shape[0])

    # 12. Database Access (Queries to databases)
    db_keywords = ["select", "insert", "update", "delete", "query", "database", "prod_db", "table"]
    db_filter = df["resource"].str.lower().str.contains("|".join(db_keywords), na=False)
    database_access = float(df[
        (df["activity_type"] == "database_query") | 
        ((df["activity_type"] == "application_access") & db_filter)
    ].shape[0])

    # 13. Website Visits (Web navigation / external connections)
    website_visits = float(df[df["activity_type"] == "network_access"].shape[0])

    # 14. External Storage Usage (USB connections and exfiltrating file writes to USB)
    usb_resource = df["resource"].str.lower().str.contains("usb|external|drive", na=False)
    external_storage_usage = float(df[
        (df["activity_type"] == "usb_connect") | 
        ((df["activity_type"] == "file_upload") & usb_resource)
    ].shape[0])

    # 15. Location (Encoded profile location)
    # 16. Department (Encoded profile department)
    # 17. Employee Role (Encoded profile designation)

    # 18. Session Duration (average duration)
    session_duration = float(df["duration"].mean()) if total_activities > 0 else 0.0

    # 19. Login Frequency (number of logins per day in target window)
    login_frequency = float(logins.shape[0]) / max(days, 1)

    # 20. Data Transfer Size (total transfers in MB)
    data_transfer_size = float(df["bytes"].sum() / 1_048_576)

    feature_vector = np.array([
        login_time,
        failed_logins,
        vpn_usage,
        usb_usage,
        file_downloads,
        file_uploads,
        email_count,
        cloud_uploads,
        device_changes,
        working_hours,
        privilege_escalation,
        database_access,
        website_visits,
        external_storage_usage,
        val_location,
        val_department,
        val_role,
        session_duration,
        login_frequency,
        data_transfer_size
    ], dtype=np.float32)

    assert len(feature_vector) == N_FEATURES
    return feature_vector
