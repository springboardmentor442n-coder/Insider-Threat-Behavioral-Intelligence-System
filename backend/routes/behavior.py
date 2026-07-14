from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from config import get_db
from crud import get_behavior_profiles

router = APIRouter()


@router.get("/behavior-profile")
def behavior_profile(db: Session = Depends(get_db)):
    return get_behavior_profiles(db)