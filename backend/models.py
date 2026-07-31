from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from backend.config import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    department = Column(String)
    password = Column(String)


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, unique=True, index=True)
    name = Column(String)
    department = Column(String)
    designation = Column(String)
    email = Column(String, unique=True)

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)

    employee_id = Column(String)

    login_count = Column(Integer)
    unique_pc_count = Column(Integer)
    is_weekend = Column(Integer)
    hour = Column(Integer)
    prediction = Column(Integer)
    risk_level = Column(String)
    confidence = Column(Float)
    event_timestamp = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)



class BehaviorFeature(Base):
    __tablename__ = "behavior_features"

    id = Column(Integer, primary_key=True, index=True)

    employee_id = Column(String, nullable=False, unique=True, index=True)

    # -------------------------
    # Login Features
    # -------------------------
    login_count = Column(Integer, default=0)
    unique_pc_count = Column(Integer, default=0)
    weekend_logins = Column(Integer, default=0)
    after_hours_logins = Column(Integer, default=0)
    average_login_hour = Column(Float, default=0)

    # -------------------------
    # HTTP Features
    # -------------------------
    http_visit_count = Column(Integer, default=0)
    unique_websites = Column(Integer, default=0)
    after_hours_http = Column(Integer, default=0)
    weekend_http = Column(Integer, default=0)
    unique_http_pcs = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    email_sent = Column(Integer, default=0)
    external_emails = Column(Integer, default=0)
    after_hours_emails = Column(Integer, default=0)
    file_access_count = Column(Integer, default=0)
    unique_files = Column(Integer, default=0)
    after_hours_file_access = Column(Integer, default=0)
    weekend_file_access = Column(Integer, default=0)
    device_usage_count = Column(Integer, default=0)
    connect_count = Column(Integer, default=0)
    disconnect_count = Column(Integer, default=0)
    after_hours_device_usage = Column(Integer, default=0)
    weekend_device_usage = Column(Integer, default=0)



class PipelineRun(Base):
    __tablename__ = "pipeline_runs"

    id = Column(Integer, primary_key=True, index=True)
    dataset_name = Column(String)
    rows_processed = Column(Integer)
    employees_processed = Column(Integer)
    high_risk = Column(Integer)
    low_risk = Column(Integer)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String)
    risk_level = Column(String)
    confidence = Column(Float)
    reason = Column(String)
    status = Column(String, default="OPEN")
    created_at = Column(DateTime, default=datetime.utcnow)