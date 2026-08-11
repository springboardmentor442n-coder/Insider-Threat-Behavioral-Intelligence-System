"""
Pydantic schemas for Employee and Employee Intelligence data.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


# ============================================================
# Existing Analytics Schemas
# ============================================================

class EmployeeSummary(BaseModel):
    user: str
    risk_score: float
    prediction: str


class EmployeeStatistics(BaseModel):
    totalEmployees: int
    averageRisk: float
    highestRisk: float
    lowestRisk: float


# ============================================================
# ML Employee Intelligence Schema
# ============================================================

class EmployeeIntelligence(BaseModel):
    """
    Employee intelligence generated from the CERT Insider
    Threat behavioral ML pipeline.

    The ML dataset uses the CERT 'user' identifier rather
    than the application database employee ID.
    """

    user: str

    risk_score: float
    risk_level: str

    rank: int

    suspicious_count: int
    consensus_percentage: float
    weighted_score: float

    isolation_forest_prediction: str
    isolation_forest_score: float

    one_class_svm_prediction: str
    one_class_svm_score: float

    lof_prediction: str
    lof_score: float

    elliptic_envelope_prediction: str
    elliptic_envelope_score: float

    pca_prediction: str
    pca_score: float

    dbscan_prediction: str
    dbscan_score: float

    kmeans_prediction: str
    kmeans_score: float


# ============================================================
# CRUD Schemas
# ============================================================

class EmployeeCreate(BaseModel):
    employee_code: str
    full_name: str
    email: str
    department: str
    designation: str


class EmployeeUpdate(BaseModel):
    employee_code: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    risk_score: Optional[float] = None
    risk_level: Optional[str] = None


class EmployeeResponse(BaseModel):
    id: int
    employee_code: str
    full_name: str
    email: str
    department: str
    designation: str
    risk_score: float
    risk_level: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
    