from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.alert import SecurityAlert
from app.schemas.alerts import AlertOut, AlertUpdate
from typing import List, Optional

router = APIRouter()

@router.get("", response_model=List[AlertOut])
def get_alerts(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(SecurityAlert)
    if status:
        query = query.filter(SecurityAlert.status.ilike(f"%{status}%"))
    if severity:
        query = query.filter(SecurityAlert.severity.ilike(f"%{severity}%"))
    
    return query.order_by(SecurityAlert.risk_score.desc()).all()

@router.patch("/{alert_id}", response_model=AlertOut)
def update_alert_status(alert_id: int, alert_in: AlertUpdate, db: Session = Depends(get_db)):
    alert = db.query(SecurityAlert).filter(SecurityAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.status = alert_in.status
    db.commit()
    db.refresh(alert)
    return alert
