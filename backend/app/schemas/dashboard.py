from pydantic import BaseModel
from typing import List, Dict, Any

class DashboardMetrics(BaseModel):
    total_user_days: int
    total_users: int
    normal_predictions: int
    suspicious_predictions: int
    critical_risks: int
    high_risks: int
    medium_risks: int
    low_risks: int
    avg_final_risk_score: float
    # Backward compatibility fields
    total_records: int
    monitored_users: int
    high_risk_users_count: int
    critical_alerts_count: int
    avg_risk_score: float
    suspicious_activities_count: int

class SeverityDistribution(BaseModel):
    Low: int
    Medium: int
    High: int
    Critical: int

class TopRiskUser(BaseModel):
    user: str
    max_risk_score: float
    severity: str
    suspicious_days: int

class RiskTrend(BaseModel):
    day: str
    avg_risk_score: float
    suspicious_count: int
