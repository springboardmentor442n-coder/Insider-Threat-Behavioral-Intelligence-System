from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime, timezone
from app.db.database import Base

class SecurityAlert(Base):
    __tablename__ = "security_alerts"

    id = Column(Integer, primary_key=True, index=True)
    user = Column(String, index=True, nullable=False)
    day = Column(String, nullable=False)
    severity = Column(String, index=True, nullable=False) # Low, Medium, High, Critical
    risk_score = Column(Float, nullable=False)
    status = Column(String, default="New", index=True) # New, In Progress, Resolved, False Positive
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
