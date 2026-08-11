from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.investigation import Investigation
from app.schemas.alerts import InvestigationOut, InvestigationCreate, InvestigationUpdate
from typing import List

router = APIRouter()

@router.get("", response_model=List[InvestigationOut])
def get_investigations(db: Session = Depends(get_db)):
    return db.query(Investigation).order_by(Investigation.updated_at.desc()).all()

@router.post("", response_model=InvestigationOut)
def create_investigation(inv_in: InvestigationCreate, db: Session = Depends(get_db)):
    inv = Investigation(
        alert_id=inv_in.alert_id,
        user=inv_in.user,
        assigned_analyst=inv_in.assigned_analyst,
        title=inv_in.title,
        summary=inv_in.summary,
        notes=inv_in.notes,
        risk_factors=inv_in.risk_factors
    )
    db.add(inv)
    db.commit()
    db.refresh(inv)
    return inv

@router.patch("/{investigation_id}", response_model=InvestigationOut)
def update_investigation(investigation_id: int, inv_in: InvestigationUpdate, db: Session = Depends(get_db)):
    inv = db.query(Investigation).filter(Investigation.id == investigation_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation case not found")
    
    if inv_in.status:
        inv.status = inv_in.status
    if inv_in.notes:
        inv.notes = f"{inv.notes}\n[{inv_in.notes}]" if inv.notes else inv_in.notes
        
    db.commit()
    db.refresh(inv)
    return inv
