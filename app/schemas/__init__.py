"""
Pydantic v2 schemas for request/response validation.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, field_validator, model_validator
from app.models import (
    UserRole, RiskCategory, AlertSeverity, AlertStatus,
    IncidentStatus, ActivityType, AnomalyType
)


# ─── Shared base ─────────────────────────────────────────────────────────────
class TimestampMixin(BaseModel):
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


# ─── Auth Schemas ─────────────────────────────────────────────────────────────
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: UserRole = UserRole.security_analyst

    @field_validator("password")
    @classmethod
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserOut(TimestampMixin):
    id: int
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    is_verified: bool
    last_login: Optional[datetime] = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


# ─── Department Schemas ───────────────────────────────────────────────────────
class DepartmentCreate(BaseModel):
    name: str
    code: str
    description: Optional[str] = None


class DepartmentOut(BaseModel):
    id: int
    name: str
    code: str
    description: Optional[str] = None
    model_config = {"from_attributes": True}


# ─── Employee Schemas ─────────────────────────────────────────────────────────
class EmployeeCreate(BaseModel):
    employee_id: str
    full_name: str
    email: EmailStr
    designation: Optional[str] = None
    department_id: Optional[int] = None
    manager_id: Optional[int] = None
    access_level: str = "standard"
    location: Optional[str] = None
    phone: Optional[str] = None
    hire_date: Optional[datetime] = None


class EmployeeUpdate(BaseModel):
    full_name: Optional[str] = None
    designation: Optional[str] = None
    department_id: Optional[int] = None
    manager_id: Optional[int] = None
    access_level: Optional[str] = None
    location: Optional[str] = None
    is_active: Optional[bool] = None
    is_terminated: Optional[bool] = None
    termination_date: Optional[datetime] = None


class EmployeeOut(TimestampMixin):
    id: int
    employee_id: str
    full_name: str
    email: str
    designation: Optional[str] = None
    department_id: Optional[int] = None
    access_level: str
    is_active: bool
    is_terminated: bool
    hire_date: Optional[datetime] = None
    location: Optional[str] = None


class EmployeeDetail(EmployeeOut):
    department: Optional[DepartmentOut] = None
    current_risk_category: Optional[RiskCategory] = None
    current_risk_score: Optional[float] = None
    open_alerts_count: int = 0


# ─── Device Schemas ───────────────────────────────────────────────────────────
class DeviceCreate(BaseModel):
    employee_id: int
    device_name: str
    device_type: str
    device_id: str
    os: Optional[str] = None
    ip_address: Optional[str] = None
    mac_address: Optional[str] = None
    is_authorized: bool = True


class DeviceOut(BaseModel):
    id: int
    employee_id: int
    device_name: str
    device_type: str
    device_id: str
    os: Optional[str] = None
    ip_address: Optional[str] = None
    is_authorized: bool
    last_seen: Optional[datetime] = None
    model_config = {"from_attributes": True}


# ─── Activity Log Schemas ─────────────────────────────────────────────────────
class ActivityLogCreate(BaseModel):
    employee_id: int
    activity_type: ActivityType
    timestamp: datetime
    source_ip: Optional[str] = None
    destination_ip: Optional[str] = None
    resource: Optional[str] = None
    bytes_transferred: Optional[int] = None
    duration_seconds: Optional[int] = None
    device_id: Optional[int] = None
    raw_log: Optional[Dict[str, Any]] = None


class ActivityLogOut(BaseModel):
    id: int
    employee_id: int
    activity_type: ActivityType
    timestamp: datetime
    source_ip: Optional[str] = None
    resource: Optional[str] = None
    bytes_transferred: Optional[int] = None
    is_outside_hours: bool
    is_suspicious: bool
    model_config = {"from_attributes": True}


class ActivityLogBulkIngest(BaseModel):
    """For CERT dataset bulk ingestion."""
    logs: List[ActivityLogCreate]


# ─── Behavioral Profile Schemas ───────────────────────────────────────────────
class BehavioralProfileOut(BaseModel):
    id: int
    employee_id: int
    avg_daily_logins: float
    avg_daily_file_accesses: float
    avg_daily_data_transfer_mb: float
    avg_daily_email_count: float
    avg_session_duration_min: float
    peer_group_id: Optional[str] = None
    baseline_days: int
    last_updated: Optional[datetime] = None
    work_hours_baseline: Optional[Dict[str, Any]] = None
    model_config = {"from_attributes": True}


# ─── Anomaly Schemas ──────────────────────────────────────────────────────────
class AnomalyOut(BaseModel):
    id: int
    employee_id: int
    anomaly_type: AnomalyType
    detected_at: datetime
    anomaly_score: float
    description: str
    is_confirmed: Optional[bool] = None
    model_name: Optional[str] = None
    features: Optional[Dict[str, Any]] = None
    model_config = {"from_attributes": True}


class AnomalyReview(BaseModel):
    is_confirmed: bool
    notes: Optional[str] = None


# ─── Risk Score Schemas ───────────────────────────────────────────────────────
class RiskScoreOut(BaseModel):
    id: int
    employee_id: int
    score_date: datetime
    behavioral_anomaly_score: float
    privilege_misuse_score: float
    data_access_violation_score: float
    access_pattern_score: float
    historical_security_score: float
    total_score: float
    risk_category: RiskCategory
    trend: str
    explanation: Optional[Dict[str, Any]] = None
    model_config = {"from_attributes": True}


class RiskSummary(BaseModel):
    employee_id: int
    employee_name: str
    current_score: float
    risk_category: RiskCategory
    trend: str
    anomaly_count_7d: int
    open_alerts: int


# ─── Alert Schemas ────────────────────────────────────────────────────────────
class AlertCreate(BaseModel):
    title: str
    description: str
    severity: AlertSeverity
    employee_id: int
    anomaly_id: Optional[int] = None
    risk_score_id: Optional[int] = None


class AlertUpdate(BaseModel):
    status: Optional[AlertStatus] = None
    notes: Optional[str] = None
    assigned_to_id: Optional[int] = None
    incident_id: Optional[int] = None


class AlertOut(BaseModel):
    id: int
    alert_id: str
    title: str
    description: str
    severity: AlertSeverity
    status: AlertStatus
    employee_id: int
    triggered_at: datetime
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    notes: Optional[str] = None
    model_config = {"from_attributes": True}


# ─── Incident Schemas ─────────────────────────────────────────────────────────
class IncidentCreate(BaseModel):
    title: str
    description: Optional[str] = None
    severity: AlertSeverity
    employee_id: Optional[int] = None
    alert_ids: Optional[List[int]] = None


class IncidentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[IncidentStatus] = None
    severity: Optional[AlertSeverity] = None
    assigned_analyst_id: Optional[int] = None
    resolution_notes: Optional[str] = None
    evidence: Optional[List[Dict[str, Any]]] = None


class IncidentOut(BaseModel):
    id: int
    incident_id: str
    title: str
    description: Optional[str] = None
    status: IncidentStatus
    severity: AlertSeverity
    employee_id: Optional[int] = None
    assigned_analyst_id: Optional[int] = None
    opened_at: datetime
    resolved_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


# ─── Dashboard Schemas ────────────────────────────────────────────────────────
class DashboardStats(BaseModel):
    total_employees_monitored: int
    critical_risk_count: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    open_alerts_count: int
    open_incidents_count: int
    anomalies_today: int
    anomalies_7d: int
    top_risk_employees: List[RiskSummary]
    alert_by_severity: Dict[str, int]
    activity_volume_24h: int


class SOCDashboard(BaseModel):
    active_threats: int
    behavioral_anomalies_today: int
    active_investigations: int
    mean_time_to_detect_hours: float
    mean_time_to_respond_hours: float
    recent_alerts: List[AlertOut]
    anomaly_trend_7d: List[Dict[str, Any]]


# ─── Report Schemas ───────────────────────────────────────────────────────────
class ReportRequest(BaseModel):
    report_type: str   # insider_threat, behavioral, investigation, compliance, risk
    start_date: datetime
    end_date: datetime
    employee_ids: Optional[List[int]] = None
    department_ids: Optional[List[int]] = None
    format: str = "json"   # json, pdf, excel


# ─── CERT Dataset Ingest ──────────────────────────────────────────────────────
class CERTLogonRecord(BaseModel):
    """Maps to CERT r4.2 logon.csv schema."""
    id: str
    date: str
    user: str
    pc: str
    activity: str   # Logon / Logoff


class CERTFileRecord(BaseModel):
    """Maps to CERT r4.2 file.csv schema."""
    id: str
    date: str
    user: str
    pc: str
    filename: str
    activity: str   # open / write / copy / delete


class CERTDeviceRecord(BaseModel):
    """Maps to CERT r4.2 device.csv schema."""
    id: str
    date: str
    user: str
    pc: str
    activity: str   # Connect / Disconnect


class CERTEmailRecord(BaseModel):
    """Maps to CERT r4.2 email.csv schema."""
    id: str
    date: str
    user: str
    pc: str
    to: str
    cc: Optional[str] = None
    bcc: Optional[str] = None
    size: int
    attachments: int
    activity: str


# ─── Pagination ───────────────────────────────────────────────────────────────
class PaginatedResponse(BaseModel):
    total: int
    page: int
    page_size: int
    data: List[Any]
