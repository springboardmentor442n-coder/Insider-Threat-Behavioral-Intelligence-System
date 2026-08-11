from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AlertOut(BaseModel):
    id: int
    user: str
    day: str
    severity: str
    risk_score: float
    status: str
    title: str
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class AlertUpdate(BaseModel):
    status: str

class InvestigationCreate(BaseModel):
    alert_id: Optional[int] = None
    user: str
    assigned_analyst: str
    title: str
    summary: Optional[str] = None
    notes: Optional[str] = None
    risk_factors: Optional[str] = None

class InvestigationOut(BaseModel):
    id: int
    alert_id: Optional[int] = None
    user: str
    assigned_analyst: str
    status: str
    title: str
    summary: Optional[str] = None
    notes: Optional[str] = None
    risk_factors: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class InvestigationUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None

class ReportSummary(BaseModel):
    generated_at: str
    total_users_monitored: int
    total_behavioral_days_analyzed: int
    normal_records_count: int
    suspicious_records_count: int
    critical_severity_count: int
    high_severity_count: int
    medium_severity_count: int
    low_severity_count: int
    top_high_risk_users: list
