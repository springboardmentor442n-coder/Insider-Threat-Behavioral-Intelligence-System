from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class PredictionRequest(BaseModel):
    logon_count: int = Field(1, ge=0)
    logoff_count: int = Field(1, ge=0)
    off_hours_logons: int = Field(0, ge=0)
    unique_pcs: int = Field(1, ge=0)
    device_connects: int = Field(0, ge=0)
    device_disconnects: int = Field(0, ge=0)
    unique_device_pcs: int = Field(0, ge=0)
    file_activity_count: int = Field(0, ge=0)
    unique_file_pcs: int = Field(0, ge=0)
    unique_files: int = Field(0, ge=0)
    sensitive_file_count: int = Field(0, ge=0)
    email_count: int = Field(0, ge=0)
    attachment_count: int = Field(0, ge=0)
    total_email_size: float = Field(0.0, ge=0.0)
    unique_email_pcs: int = Field(0, ge=0)
    external_email_count: int = Field(0, ge=0)
    http_request_count: int = Field(0, ge=0)
    unique_http_urls: int = Field(0, ge=0)
    off_hours_http: int = Field(0, ge=0)

class PredictionResponse(BaseModel):
    prediction: int
    prediction_probability: float
    ml_risk_score: float
    behavioral_risk_score: float
    final_risk_score: float
    severity: str
    features_used: List[str]
