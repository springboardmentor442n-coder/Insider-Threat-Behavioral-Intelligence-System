"""
CRUD Operations
Investigation Module
"""

from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.database.models import (
    Employee,
    Activity,
    Risk,
    Threat,
)


# ============================================================
# Employee
# ============================================================

def get_employee(db: Session, employee_id: int):
    return (
        db.query(Employee)
        .filter(Employee.id == employee_id)
        .first()
    )


# ============================================================
# Activities
# ============================================================

def get_employee_activities(
    db: Session,
    employee_id: int,
):

    return (
        db.query(Activity)
        .filter(Activity.employee_id == employee_id)
        .order_by(desc(Activity.timestamp))
        .all()
    )


# ============================================================
# Risks
# ============================================================

def get_employee_risk_history(
    db: Session,
    employee_id: int,
):

    return (
        db.query(Risk)
        .filter(Risk.employee_id == employee_id)
        .order_by(desc(Risk.created_at))
        .all()
    )


# ============================================================
# Threats
# ============================================================

def get_employee_threats(
    db: Session,
    employee_id: int,
):

    return (
        db.query(Threat)
        .filter(Threat.employee_id == employee_id)
        .order_by(desc(Threat.created_at))
        .all()
    )


# ============================================================
# Investigation Summary
# ============================================================

def get_employee_investigation(
    db: Session,
    employee_id: int,
):

    employee = get_employee(
        db,
        employee_id,
    )

    if employee is None:
        return None

    activities = get_employee_activities(
        db,
        employee_id,
    )

    risks = get_employee_risk_history(
        db,
        employee_id,
    )

    threats = get_employee_threats(
        db,
        employee_id,
    )

    return {
        "employee": employee,
        "activities": activities,
        "risks": risks,
        "threats": threats,
    }
