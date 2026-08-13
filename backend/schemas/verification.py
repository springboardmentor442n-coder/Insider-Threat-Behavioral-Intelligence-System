"""
Pydantic schemas for Custom Employee Evaluation and Verification endpoints.
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class CustomEmployeeEvaluationRequest(BaseModel):
    user: Optional[str] = "EMP_CUSTOM"
    user_id: Optional[str] = None
    name: Optional[str] = "Custom Employee"
    department: Optional[str] = "Engineering"
    role: Optional[str] = "Staff"
    email: Optional[str] = None

    # Behavioral Features
    after_hours_activity: float = 0.0
    midnight_activity: float = 0.0
    weekend_activity: float = 0.0
    device_events: float = 0.0
    file_events: float = 0.0
    unique_files: float = 0.0
    unique_pcs: float = 1.0
    web_events: float = 0.0
    unique_urls: float = 0.0
    emails_sent: float = 0.0
    total_events: float = 0.0
    active_days: float = 100.0
    unique_sources: float = 3.0
    total_logins: float = 100.0
    average_hour: float = 12.0
    earliest_hour: float = 7.0
    latest_hour: float = 18.0
    openness: float = 30.0
    conscientiousness: float = 30.0
    extraversion: float = 30.0
    agreeableness: float = 30.0
    neuroticism: float = 30.0


class CustomEmployeeEvaluationResponse(BaseModel):
    disclaimer: str
    user: str
    employee_id: str
    name: str
    department: str
    role: str
    risk_score: float
    weighted_score: float
    risk_level: str
    rank: int
    suspicious_model_count: int
    consensus_percentage: float
    supported_by_behavioral_evidence: bool
    anomalous_vector_count: int
    total_vectors_tested: int
    model_predictions: Dict[str, str]
    behavioral_vectors: List[Dict[str, Any]]
    raw_features: Dict[str, Any]
