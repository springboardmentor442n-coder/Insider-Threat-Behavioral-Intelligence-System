from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime, timezone
from app.db.database import Base

class Investigation(Base):
    __tablename__ = "investigations"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, nullable=True)
    user = Column(String, index=True, nullable=False)
    assigned_analyst = Column(String, nullable=False)
    status = Column(String, default="Open", index=True) # Open, In Progress, Closed, Escalate
    title = Column(String, nullable=False)
    summary = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    risk_factors = Column(String, nullable=True) # Comma separated indicators
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    analyst_name = Column(String, nullable=False)
    action = Column(String, nullable=False)
    details = Column(String, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
