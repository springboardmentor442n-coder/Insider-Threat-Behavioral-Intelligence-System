from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.config import get_db
from backend.crud import (
    get_behavior_profiles,
    get_employee_profile
)

router = APIRouter(
    prefix="/behavior",
    tags=["Behavior"]
)


@router.get("/")
def behavior_profiles(
    db: Session = Depends(get_db)
):
    return get_behavior_profiles(db)


@router.get("/{employee_id}")
def employee_profile(
    employee_id: str,
    db: Session = Depends(get_db)
):
    return get_employee_profile(
        db,
        employee_id
    )