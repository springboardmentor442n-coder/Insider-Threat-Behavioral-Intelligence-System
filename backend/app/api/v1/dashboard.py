from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.database import get_db
from app.models.risk_record import BehavioralRiskRecord
from app.models.alert import SecurityAlert
from app.schemas.dashboard import DashboardMetrics, SeverityDistribution, TopRiskUser, RiskTrend
from typing import List

router = APIRouter()

@router.get("/metrics", response_model=DashboardMetrics)
def get_dashboard_metrics(db: Session = Depends(get_db)):
    total_user_days = db.query(BehavioralRiskRecord).count()
    total_users = db.query(func.count(func.distinct(BehavioralRiskRecord.user))).scalar() or 0
    
    normal_predictions = db.query(BehavioralRiskRecord).filter(BehavioralRiskRecord.prediction == 0).count()
    suspicious_predictions = db.query(BehavioralRiskRecord).filter(BehavioralRiskRecord.prediction == 1).count()

    critical_risks = db.query(BehavioralRiskRecord).filter(BehavioralRiskRecord.severity == "Critical").count()
    high_risks = db.query(BehavioralRiskRecord).filter(BehavioralRiskRecord.severity == "High").count()
    medium_risks = db.query(BehavioralRiskRecord).filter(BehavioralRiskRecord.severity == "Medium").count()
    low_risks = db.query(BehavioralRiskRecord).filter(BehavioralRiskRecord.severity == "Low").count()

    avg_final_risk_score = db.query(func.avg(BehavioralRiskRecord.final_risk_score)).scalar() or 0.0

    high_risk_users_count = db.query(func.count(func.distinct(BehavioralRiskRecord.user))).filter(
        BehavioralRiskRecord.severity.in_(["High", "Critical"])
    ).scalar() or 0
    critical_alerts_count = db.query(SecurityAlert).filter(SecurityAlert.severity == "Critical").count()

    return {
        "total_user_days": total_user_days,
        "total_users": total_users,
        "normal_predictions": normal_predictions,
        "suspicious_predictions": suspicious_predictions,
        "critical_risks": critical_risks,
        "high_risks": high_risks,
        "medium_risks": medium_risks,
        "low_risks": low_risks,
        "avg_final_risk_score": round(avg_final_risk_score, 2),

        # Backward compatibility
        "total_records": total_user_days,
        "monitored_users": total_users,
        "high_risk_users_count": high_risk_users_count,
        "critical_alerts_count": critical_alerts_count,
        "avg_risk_score": round(avg_final_risk_score, 2),
        "suspicious_activities_count": suspicious_predictions
    }

@router.get("/severity-distribution", response_model=SeverityDistribution)
def get_severity_distribution(db: Session = Depends(get_db)):
    low = db.query(BehavioralRiskRecord).filter(BehavioralRiskRecord.severity == "Low").count()
    medium = db.query(BehavioralRiskRecord).filter(BehavioralRiskRecord.severity == "Medium").count()
    high = db.query(BehavioralRiskRecord).filter(BehavioralRiskRecord.severity == "High").count()
    critical = db.query(BehavioralRiskRecord).filter(BehavioralRiskRecord.severity == "Critical").count()

    return {
        "Low": low,
        "Medium": medium,
        "High": high,
        "Critical": critical
    }

@router.get("/top-risk-users", response_model=List[TopRiskUser])
def get_top_risk_users(db: Session = Depends(get_db)):
    results = db.query(
        BehavioralRiskRecord.user,
        func.max(BehavioralRiskRecord.final_risk_score).label("max_score"),
        func.count(BehavioralRiskRecord.id).label("total_days")
    ).group_by(BehavioralRiskRecord.user).order_by(func.max(BehavioralRiskRecord.final_risk_score).desc()).limit(10).all()

    top_users = []
    for u, max_score, total_days in results:
        latest = db.query(BehavioralRiskRecord).filter(BehavioralRiskRecord.user == u).order_by(BehavioralRiskRecord.final_risk_score.desc()).first()
        susp_count = db.query(BehavioralRiskRecord).filter(BehavioralRiskRecord.user == u, BehavioralRiskRecord.prediction == 1).count()
        top_users.append({
            "user": u,
            "max_risk_score": round(max_score, 2),
            "severity": latest.severity if latest else "Low",
            "suspicious_days": susp_count
        })
    return top_users

@router.get("/risk-trends", response_model=List[RiskTrend])
def get_risk_trends(db: Session = Depends(get_db)):
    results = db.query(
        BehavioralRiskRecord.day,
        func.avg(BehavioralRiskRecord.final_risk_score).label("avg_score"),
        func.sum(BehavioralRiskRecord.prediction).label("susp_count")
    ).group_by(BehavioralRiskRecord.day).order_by(BehavioralRiskRecord.day.asc()).limit(30).all()

    return [
        {
            "day": day,
            "avg_risk_score": round(avg_score or 0.0, 2),
            "suspicious_count": int(susp_count or 0)
        }
        for day, avg_score, susp_count in results
    ]
