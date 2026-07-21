from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.config import get_db

from backend.crud import (
    get_dashboard_stats,
    get_department_statistics,
    get_risk_distribution,
    get_login_hour_distribution,
    get_top_risk_employees,
    get_recent_alerts,
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats")
def dashboard_stats(db: Session = Depends(get_db)):
    return get_dashboard_stats(db)


@router.get("/departments")
def department_statistics(db: Session = Depends(get_db)):
    return get_department_statistics(db)


@router.get("/risk-distribution")
def risk_distribution(db: Session = Depends(get_db)):
    return get_risk_distribution(db)


@router.get("/login-hours")
def login_hours(db: Session = Depends(get_db)):
    return get_login_hour_distribution(db)


@router.get("/top-risk")
def top_risk(db: Session = Depends(get_db)):
    return get_top_risk_employees(db)


@router.get("/recent-alerts")
def recent_alerts(db: Session = Depends(get_db)):
    return get_recent_alerts(db)