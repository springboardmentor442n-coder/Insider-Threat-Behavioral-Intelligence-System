from sqlalchemy import Column, Integer, String, Float, Date
from app.db.database import Base

class BehavioralRiskRecord(Base):
    __tablename__ = "behavioral_risk_records"

    id = Column(Integer, primary_key=True, index=True)
    user = Column(String, index=True, nullable=False)
    day = Column(String, index=True, nullable=False)
    
    # 19 Behavioral Features
    logon_count = Column(Integer, default=0)
    logoff_count = Column(Integer, default=0)
    off_hours_logons = Column(Integer, default=0)
    unique_pcs = Column(Integer, default=0)
    
    device_connects = Column(Integer, default=0)
    device_disconnects = Column(Integer, default=0)
    unique_device_pcs = Column(Integer, default=0)
    
    file_activity_count = Column(Integer, default=0)
    unique_file_pcs = Column(Integer, default=0)
    unique_files = Column(Integer, default=0)
    sensitive_file_count = Column(Integer, default=0)
    
    email_count = Column(Integer, default=0)
    attachment_count = Column(Integer, default=0)
    total_email_size = Column(Float, default=0.0)
    unique_email_pcs = Column(Integer, default=0)
    external_email_count = Column(Integer, default=0)
    
    http_request_count = Column(Integer, default=0)
    unique_http_urls = Column(Integer, default=0)
    off_hours_http = Column(Integer, default=0)
    
    # Machine Learning & Risk Scoring Outputs
    prediction = Column(Integer, default=0) # 0: Normal, 1: Suspicious
    prediction_probability = Column(Float, default=0.0)
    ml_risk_score = Column(Float, default=0.0)
    behavioral_risk_score = Column(Float, default=0.0)
    final_risk_score = Column(Float, default=0.0)
    severity = Column(String, index=True, default="Low") # Low, Medium, High, Critical
