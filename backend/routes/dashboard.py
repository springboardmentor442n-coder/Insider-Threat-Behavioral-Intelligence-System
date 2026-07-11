from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.config import get_db
from database.crud import get_dashboard_stats

router = APIRouter()

@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db)):
    return get_dashboard_stats(db)