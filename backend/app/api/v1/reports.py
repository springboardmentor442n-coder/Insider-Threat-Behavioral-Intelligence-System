from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone
from app.db.database import get_db
from app.models.risk_record import BehavioralRiskRecord
from app.schemas.alerts import ReportSummary

router = APIRouter()

@router.get("/summary", response_model=ReportSummary)
def get_report_summary(db: Session = Depends(get_db)):
    total_users = db.query(func.count(func.distinct(BehavioralRiskRecord.user))).scalar() or 0
    total_records = db.query(BehavioralRiskRecord).count()
    normal_count = db.query(BehavioralRiskRecord).filter(BehavioralRiskRecord.prediction == 0).count()
    suspicious_count = db.query(BehavioralRiskRecord).filter(BehavioralRiskRecord.prediction == 1).count()

    critical_count = db.query(BehavioralRiskRecord).filter(BehavioralRiskRecord.severity == "Critical").count()
    high_count = db.query(BehavioralRiskRecord).filter(BehavioralRiskRecord.severity == "High").count()
    medium_count = db.query(BehavioralRiskRecord).filter(BehavioralRiskRecord.severity == "Medium").count()
    low_count = db.query(BehavioralRiskRecord).filter(BehavioralRiskRecord.severity == "Low").count()

    top_users_query = db.query(
        BehavioralRiskRecord.user,
        func.max(BehavioralRiskRecord.final_risk_score).label("score")
    ).group_by(BehavioralRiskRecord.user).order_by(func.max(BehavioralRiskRecord.final_risk_score).desc()).limit(10).all()

    top_users = [{"user": u, "max_score": round(s, 2)} for u, s in top_users_query]

    return {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "total_users_monitored": total_users,
        "total_behavioral_days_analyzed": total_records,
        "normal_records_count": normal_count,
        "suspicious_records_count": suspicious_count,
        "critical_severity_count": critical_count,
        "high_severity_count": high_count,
        "medium_severity_count": medium_count,
        "low_severity_count": low_count,
        "top_high_risk_users": top_users
    }
