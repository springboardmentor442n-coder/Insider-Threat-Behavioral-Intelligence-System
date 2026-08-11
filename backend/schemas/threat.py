"""
Pydantic schemas for Threat Center.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


# ============================================================
# Base Schema
# ============================================================

class ThreatBase(BaseModel):
    employee_id: int
    employee_name: str
    department: str
    risk_score: float
    severity: str
    status: str
    threat_type: str
    description: str
    evidence: Optional[str] = ""
    models_triggered: Optional[str] = ""


# ============================================================
# Create
# ============================================================

class ThreatCreate(ThreatBase):
    pass


# ============================================================
# Update
# ============================================================

class ThreatUpdate(BaseModel):
    risk_score: Optional[float] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    threat_type: Optional[str] = None
    description: Optional[str] = None
    evidence: Optional[str] = None
    models_triggered: Optional[str] = None


# ============================================================
# Response
# ============================================================

class ThreatResponse(ThreatBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
    