from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.database import get_db
from app.models.risk_record import BehavioralRiskRecord
from app.schemas.users import UserSummary, BehavioralRiskRecordOut
from typing import List, Optional

router = APIRouter()

@router.get("", response_model=List[UserSummary])
def get_monitored_users(
    search: Optional[str] = None,
    severity: Optional[str] = None,
    prediction: Optional[int] = None,
    sort: Optional[str] = "highest_risk",
    minRisk: Optional[float] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    query = db.query(
        BehavioralRiskRecord.user,
        func.count(BehavioralRiskRecord.id).label("record_count"),
        func.max(BehavioralRiskRecord.final_risk_score).label("max_risk_score"),
        func.sum(BehavioralRiskRecord.off_hours_logons).label("total_off_hours_logons"),
        func.sum(BehavioralRiskRecord.device_connects).label("total_device_connects"),
        func.sum(BehavioralRiskRecord.sensitive_file_count).label("total_sensitive_files"),
        func.sum(BehavioralRiskRecord.external_email_count).label("total_external_emails")
    ).group_by(BehavioralRiskRecord.user)

    if search:
        query = query.filter(BehavioralRiskRecord.user.ilike(f"%{search}%"))

    if prediction is not None:
        query = query.filter(BehavioralRiskRecord.prediction == prediction)

    if minRisk is not None:
        query = query.filter(BehavioralRiskRecord.final_risk_score >= minRisk)

    if sort == "lowest_risk":
        query = query.order_by(func.max(BehavioralRiskRecord.final_risk_score).asc())
    else:
        query = query.order_by(func.max(BehavioralRiskRecord.final_risk_score).desc())

    results = query.offset(offset).limit(limit).all()

    user_summaries = []
    for r in results:
        latest = db.query(BehavioralRiskRecord).filter(BehavioralRiskRecord.user == r.user).order_by(BehavioralRiskRecord.final_risk_score.desc()).first()
        
        if severity and latest and latest.severity.lower() != severity.lower():
            continue

        user_summaries.append({
            "user": r.user,
            "record_count": r.record_count,
            "max_risk_score": round(r.max_risk_score, 2),
            "latest_severity": latest.severity if latest else "Low",
            "total_off_hours_logons": int(r.total_off_hours_logons or 0),
            "total_device_connects": int(r.total_device_connects or 0),
            "total_sensitive_files": int(r.total_sensitive_files or 0),
            "total_external_emails": int(r.total_external_emails or 0)
        })

    return user_summaries

@router.get("/{user_id}", response_model=UserSummary)
def get_user_by_id(user_id: str, db: Session = Depends(get_db)):
    r = db.query(
        BehavioralRiskRecord.user,
        func.count(BehavioralRiskRecord.id).label("record_count"),
        func.max(BehavioralRiskRecord.final_risk_score).label("max_risk_score"),
        func.sum(BehavioralRiskRecord.off_hours_logons).label("total_off_hours_logons"),
        func.sum(BehavioralRiskRecord.device_connects).label("total_device_connects"),
        func.sum(BehavioralRiskRecord.sensitive_file_count).label("total_sensitive_files"),
        func.sum(BehavioralRiskRecord.external_email_count).label("total_external_emails")
    ).filter(BehavioralRiskRecord.user == user_id).group_by(BehavioralRiskRecord.user).first()

    if not r:
        raise HTTPException(status_code=404, detail=f"User ID {user_id} not found.")

    latest = db.query(BehavioralRiskRecord).filter(BehavioralRiskRecord.user == user_id).order_by(BehavioralRiskRecord.final_risk_score.desc()).first()

    return {
        "user": r.user,
        "record_count": r.record_count,
        "max_risk_score": round(r.max_risk_score, 2),
        "latest_severity": latest.severity if latest else "Low",
        "total_off_hours_logons": int(r.total_off_hours_logons or 0),
        "total_device_connects": int(r.total_device_connects or 0),
        "total_sensitive_files": int(r.total_sensitive_files or 0),
        "total_external_emails": int(r.total_external_emails or 0)
    }

@router.get("/{user_id}/history", response_model=List[BehavioralRiskRecordOut])
def get_user_history(user_id: str, db: Session = Depends(get_db)):
    records = db.query(BehavioralRiskRecord).filter(BehavioralRiskRecord.user == user_id).order_by(BehavioralRiskRecord.day.asc()).all()
    if not records:
        raise HTTPException(status_code=404, detail=f"No activity records found for user ID: {user_id}")
    return records

@router.get("/{user_id}/behavior")
def get_user_behavior(user_id: str, db: Session = Depends(get_db)):
    records = db.query(BehavioralRiskRecord).filter(BehavioralRiskRecord.user == user_id).all()
    if not records:
        raise HTTPException(status_code=404, detail=f"No behavior records found for user ID: {user_id}")

    total_logons = sum(r.logon_count for r in records)
    off_hours_logons = sum(r.off_hours_logons for r in records)
    total_connects = sum(r.device_connects for r in records)
    total_disconnects = sum(r.device_disconnects for r in records)
    total_files = sum(r.file_activity_count for r in records)
    sensitive_files = sum(r.sensitive_file_count for r in records)
    total_emails = sum(r.email_count for r in records)
    external_emails = sum(r.external_email_count for r in records)
    attachments = sum(r.attachment_count for r in records)
    total_http = sum(r.http_request_count for r in records)
    off_hours_http = sum(r.off_hours_http for r in records)

    return {
        "user": user_id,
        "days_monitored": len(records),
        "logon": {
            "total_logons": total_logons,
            "off_hours_logons": off_hours_logons,
            "off_hours_ratio": round(off_hours_logons / max(1, total_logons), 4)
        },
        "device": {
            "total_connects": total_connects,
            "total_disconnects": total_disconnects
        },
        "file": {
            "total_file_activities": total_files,
            "sensitive_file_count": sensitive_files,
            "sensitive_ratio": round(sensitive_files / max(1, total_files), 4)
        },
        "email": {
            "total_emails": total_emails,
            "external_emails": external_emails,
            "attachment_count": attachments
        },
        "http": {
            "total_http_requests": total_http,
            "off_hours_http": off_hours_http
        }
    }
