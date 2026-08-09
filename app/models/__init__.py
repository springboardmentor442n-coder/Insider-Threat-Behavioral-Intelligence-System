"""
All SQLAlchemy ORM models for the Insider Threat Behavioral Intelligence System.
"""
from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Text, Enum,
    ForeignKey, JSON, Index, BigInteger
)
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


def utcnow():
    return datetime.now(timezone.utc)


# ─── Enums ────────────────────────────────────────────────────────────────────
class UserRole(str, enum.Enum):
    security_analyst = "security_analyst"
    soc_engineer = "soc_engineer"
    security_manager = "security_manager"
    administrator = "administrator"


class RiskCategory(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class AlertSeverity(str, enum.Enum):
    informational = "informational"
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class AlertStatus(str, enum.Enum):
    open = "open"
    acknowledged = "acknowledged"
    investigating = "investigating"
    resolved = "resolved"
    false_positive = "false_positive"


class IncidentStatus(str, enum.Enum):
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"
    closed = "closed"


class ActivityType(str, enum.Enum):
    login = "login"
    logout = "logout"
    file_download = "file_download"
    file_upload = "file_upload"
    file_delete = "file_delete"
    email_send = "email_send"
    email_receive = "email_receive"
    usb_connect = "usb_connect"
    usb_disconnect = "usb_disconnect"
    remote_access = "remote_access"
    privilege_change = "privilege_change"
    data_transfer = "data_transfer"
    application_access = "application_access"
    network_access = "network_access"
    failed_login = "failed_login"
    database_query = "database_query"


class AnomalyType(str, enum.Enum):
    unusual_login_time = "unusual_login_time"
    abnormal_data_download = "abnormal_data_download"
    unauthorized_access = "unauthorized_access"
    excessive_file_transfer = "excessive_file_transfer"
    suspicious_device = "suspicious_device"
    privilege_abuse = "privilege_abuse"
    data_exfiltration = "data_exfiltration"
    peer_deviation = "peer_deviation"


# ─── Module 1: User Authentication ───────────────────────────────────────────
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.security_analyst, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    # Relationships
    assigned_incidents = relationship("Incident", back_populates="assigned_analyst")
    audit_logs = relationship("AuditLog", back_populates="user")

    __table_args__ = (Index("ix_users_email_active", "email", "is_active"),)


# ─── Module 2: Employee Identity & Profile ────────────────────────────────────
class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    employees = relationship("Employee", back_populates="department")


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String(100), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    designation = Column(String(255), nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    manager_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    is_terminated = Column(Boolean, default=False)
    termination_date = Column(DateTime(timezone=True), nullable=True)
    hire_date = Column(DateTime(timezone=True), nullable=True)
    access_level = Column(String(50), default="standard")
    location = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    # Relationships
    department = relationship("Department", back_populates="employees")
    manager = relationship("Employee", remote_side=[id])
    devices = relationship("Device", back_populates="employee")
    activities = relationship("ActivityLog", back_populates="employee")
    behavioral_profile = relationship("BehavioralProfile", back_populates="employee", uselist=False)
    anomalies = relationship("Anomaly", back_populates="employee")
    risk_scores = relationship("RiskScore", back_populates="employee")
    alerts = relationship("Alert", back_populates="employee")

    __table_args__ = (
        Index("ix_employees_dept_active", "department_id", "is_active"),
        Index("ix_employees_terminated", "is_terminated"),
    )


class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    device_name = Column(String(255), nullable=False)
    device_type = Column(String(100), nullable=False)   # laptop, desktop, mobile, usb
    device_id = Column(String(255), unique=True, nullable=False)
    os = Column(String(100), nullable=True)
    ip_address = Column(String(45), nullable=True)
    mac_address = Column(String(50), nullable=True)
    is_authorized = Column(Boolean, default=True)
    last_seen = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    employee = relationship("Employee", back_populates="devices")


# ─── Module 3: Activity Monitoring ───────────────────────────────────────────
class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(BigInteger, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    activity_type = Column(Enum(ActivityType), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    source_ip = Column(String(45), nullable=True)
    destination_ip = Column(String(45), nullable=True)
    resource = Column(String(500), nullable=True)        # file path, URL, app name
    bytes_transferred = Column(BigInteger, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=True)
    is_outside_hours = Column(Boolean, default=False)
    is_suspicious = Column(Boolean, default=False)
    raw_log = Column(JSON, nullable=True)                # original CERT log fields
    created_at = Column(DateTime(timezone=True), default=utcnow)

    # Relationships
    employee = relationship("Employee", back_populates="activities")
    device = relationship("Device")

    __table_args__ = (
        Index("ix_activity_employee_timestamp", "employee_id", "timestamp"),
        Index("ix_activity_type_timestamp", "activity_type", "timestamp"),
        Index("ix_activity_suspicious", "is_suspicious", "timestamp"),
    )


# ─── Module 4: Behavioral Profiling ──────────────────────────────────────────
class BehavioralProfile(Base):
    __tablename__ = "behavioral_profiles"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), unique=True, nullable=False)

    # Work hour baseline (JSON: {"start": 8, "end": 18, "days": [0,1,2,3,4]})
    work_hours_baseline = Column(JSON, nullable=True)

    # Resource access frequency stats
    avg_daily_logins = Column(Float, default=0.0)
    avg_daily_file_accesses = Column(Float, default=0.0)
    avg_daily_data_transfer_mb = Column(Float, default=0.0)
    avg_daily_email_count = Column(Float, default=0.0)
    avg_daily_app_count = Column(Float, default=0.0)
    avg_session_duration_min = Column(Float, default=0.0)

    # Standard deviations for anomaly thresholds
    std_daily_logins = Column(Float, default=0.0)
    std_daily_file_accesses = Column(Float, default=0.0)
    std_daily_data_transfer_mb = Column(Float, default=0.0)

    # Access pattern features
    top_accessed_resources = Column(JSON, nullable=True)    # top 20 resources
    typical_source_ips = Column(JSON, nullable=True)
    typical_devices = Column(JSON, nullable=True)
    peer_group_id = Column(String(100), nullable=True)      # for UEBA peer grouping

    baseline_days = Column(Integer, default=0)              # days used to build baseline
    last_updated = Column(DateTime(timezone=True), default=utcnow)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    employee = relationship("Employee", back_populates="behavioral_profile")


# ─── Module 5: Anomaly Detection ─────────────────────────────────────────────
class Anomaly(Base):
    __tablename__ = "anomalies"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    activity_log_id = Column(BigInteger, ForeignKey("activity_logs.id"), nullable=True)
    anomaly_type = Column(Enum(AnomalyType), nullable=False)
    detected_at = Column(DateTime(timezone=True), default=utcnow, index=True)
    anomaly_score = Column(Float, nullable=False)           # 0–1, higher = more anomalous
    description = Column(Text, nullable=False)
    features = Column(JSON, nullable=True)                  # feature values that triggered detection
    is_confirmed = Column(Boolean, nullable=True)           # None = unreviewed
    model_name = Column(String(100), nullable=True)         # which model detected it
    created_at = Column(DateTime(timezone=True), default=utcnow)

    employee = relationship("Employee", back_populates="anomalies")
    activity_log = relationship("ActivityLog")

    __table_args__ = (
        Index("ix_anomaly_employee_detected", "employee_id", "detected_at"),
        Index("ix_anomaly_type_score", "anomaly_type", "anomaly_score"),
    )


# ─── Module 6: Insider Risk Scoring ──────────────────────────────────────────
class RiskScore(Base):
    __tablename__ = "risk_scores"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    score_date = Column(DateTime(timezone=True), default=utcnow, index=True)

    # Weighted component scores (0–100 each)
    behavioral_anomaly_score = Column(Float, default=0.0)
    privilege_misuse_score = Column(Float, default=0.0)
    data_access_violation_score = Column(Float, default=0.0)
    access_pattern_score = Column(Float, default=0.0)
    historical_security_score = Column(Float, default=0.0)

    # Final weighted score (0–100)
    total_score = Column(Float, nullable=False)
    risk_category = Column(Enum(RiskCategory), nullable=False)

    # Hybrid ML outputs
    isolation_forest_score = Column(Float, nullable=True)
    xgboost_probability = Column(Float, nullable=True)

    # Score explanations
    explanation = Column(JSON, nullable=True)              # {"top_factors": [...]}
    trend = Column(String(20), default="stable")          # increasing, decreasing, stable

    created_at = Column(DateTime(timezone=True), default=utcnow)

    employee = relationship("Employee", back_populates="risk_scores")

    __table_args__ = (
        Index("ix_risk_employee_date", "employee_id", "score_date"),
        Index("ix_risk_category_date", "risk_category", "score_date"),
    )


# ─── Module 7: Threat Investigation ──────────────────────────────────────────
class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(String(50), unique=True, nullable=False)  # INC-2024-001
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(IncidentStatus), default=IncidentStatus.open, nullable=False)
    severity = Column(Enum(AlertSeverity), nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    assigned_analyst_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    evidence = Column(JSON, nullable=True)                 # list of evidence items
    timeline = Column(JSON, nullable=True)                 # reconstructed event timeline
    resolution_notes = Column(Text, nullable=True)
    opened_at = Column(DateTime(timezone=True), default=utcnow)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    assigned_analyst = relationship("User", back_populates="assigned_incidents")
    alerts = relationship("Alert", back_populates="incident")

    __table_args__ = (Index("ix_incident_status_severity", "status", "severity"),)


# ─── Module 9: Alerts ────────────────────────────────────────────────────────
class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(String(50), unique=True, nullable=False)  # ALT-2024-001
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(Enum(AlertSeverity), nullable=False, index=True)
    status = Column(Enum(AlertStatus), default=AlertStatus.open, nullable=False, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=True)
    anomaly_id = Column(Integer, ForeignKey("anomalies.id"), nullable=True)
    risk_score_id = Column(Integer, ForeignKey("risk_scores.id"), nullable=True)
    triggered_at = Column(DateTime(timezone=True), default=utcnow, index=True)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    employee = relationship("Employee", back_populates="alerts")
    incident = relationship("Incident", back_populates="alerts")
    anomaly = relationship("Anomaly")

    __table_args__ = (
        Index("ix_alert_employee_triggered", "employee_id", "triggered_at"),
        Index("ix_alert_severity_status", "severity", "status"),
    )


# ─── Audit Log ────────────────────────────────────────────────────────────────
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(255), nullable=False)
    resource_type = Column(String(100), nullable=True)
    resource_id = Column(String(100), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    details = Column(JSON, nullable=True)
    timestamp = Column(DateTime(timezone=True), default=utcnow, index=True)

    user = relationship("User", back_populates="audit_logs")
