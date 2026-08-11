"""
SQLAlchemy ORM Models
"""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)

from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base


# ============================================================
# User
# ============================================================

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    username: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    role: Mapped[str] = mapped_column(
        String(50),
        default="Employee",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )


# ============================================================
# Employee
# ============================================================

class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    employee_code: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        nullable=False,
    )

    full_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        nullable=False,
    )

    department: Mapped[str] = mapped_column(
        String(100),
    )

    designation: Mapped[str] = mapped_column(
        String(100),
    )

    risk_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )

    risk_level: Mapped[str] = mapped_column(
        String(20),
        default="Low",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    activities = relationship(
        "Activity",
        back_populates="employee",
        cascade="all, delete",
    )

    risks = relationship(
        "Risk",
        back_populates="employee",
        cascade="all, delete",
    )


# ============================================================
# Activity
# ============================================================

class Activity(Base):
    __tablename__ = "activities"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    employee_id: Mapped[int] = mapped_column(
        ForeignKey("employees.id"),
    )

    activity_type: Mapped[str] = mapped_column(
        String(100),
    )

    description: Mapped[str] = mapped_column(
        Text,
    )

    severity: Mapped[str] = mapped_column(
        String(20),
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    employee = relationship(
        "Employee",
        back_populates="activities",
    )


# ============================================================
# Risk
# ============================================================

class Risk(Base):
    __tablename__ = "risk_scores"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    employee_id: Mapped[int] = mapped_column(
        ForeignKey("employees.id"),
    )

    score: Mapped[float] = mapped_column(
        Float,
    )

    prediction: Mapped[str] = mapped_column(
        String(50),
    )

    model_name: Mapped[str] = mapped_column(
        String(100),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    employee = relationship(
        "Employee",
        back_populates="risks",
    )


# ============================================================
# Reports
# ============================================================

class Report(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    report_name: Mapped[str] = mapped_column(
        String(200),
    )

    report_type: Mapped[str] = mapped_column(
        String(50),
    )

    file_path: Mapped[str] = mapped_column(
        String(500),
    )

    generated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )


# ============================================================
# ML Models
# ============================================================

class MLModel(Base):
    __tablename__ = "ml_models"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    model_name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
    )

    algorithm: Mapped[str] = mapped_column(
        String(100),
    )

    accuracy: Mapped[float] = mapped_column(
        Float,
    )

    precision: Mapped[float] = mapped_column(
        Float,
    )

    recall: Mapped[float] = mapped_column(
        Float,
    )

    f1_score: Mapped[float] = mapped_column(
        Float,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

# ============================================================
# Threat
# ============================================================

class Threat(Base):
    __tablename__ = "threats"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    employee_id: Mapped[int] = mapped_column(
        ForeignKey("employees.id"),
        nullable=False,
    )

    employee_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    department: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    risk_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )

    severity: Mapped[str] = mapped_column(
        String(20),
        default="Low",
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="Open",
    )

    threat_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    evidence: Mapped[str] = mapped_column(
        Text,
        default="",
    )

    models_triggered: Mapped[str] = mapped_column(
        String(255),
        default="",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    employee = relationship("Employee")
    