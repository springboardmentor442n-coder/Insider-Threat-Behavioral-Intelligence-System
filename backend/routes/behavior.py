from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.config import get_db
from backend.crud import get_behavior_profiles

router = APIRouter()


@router.get("/behavior-profile")
def read_behavior_profiles(db: Session = Depends(get_db)):
    return get_behavior_profiles(db)