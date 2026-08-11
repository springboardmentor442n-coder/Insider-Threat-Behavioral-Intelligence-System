from pydantic import BaseModel
from typing import List, Optional

class BehavioralRiskRecordOut(BaseModel):
    id: int
    user: str
    day: str
    logon_count: int
    logoff_count: int
    off_hours_logons: int
    unique_pcs: int
    device_connects: int
    device_disconnects: int
    unique_device_pcs: int
    file_activity_count: int
    unique_file_pcs: int
    unique_files: int
    sensitive_file_count: int
    email_count: int
    attachment_count: int
    total_email_size: float
    unique_email_pcs: int
    external_email_count: int
    http_request_count: int
    unique_http_urls: int
    off_hours_http: int
    prediction: int
    prediction_probability: float
    ml_risk_score: float
    behavioral_risk_score: float
    final_risk_score: float
    severity: str

    class Config:
        from_attributes = True

class UserSummary(BaseModel):
    user: str
    record_count: int
    max_risk_score: float
    latest_severity: str
    total_off_hours_logons: int
    total_device_connects: int
    total_sensitive_files: int
    total_external_emails: int
