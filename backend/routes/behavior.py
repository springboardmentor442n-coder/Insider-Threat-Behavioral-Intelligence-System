from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.config import get_db
from backend.crud import get_behavior_features

router = APIRouter(
    prefix="/behavior",
    tags=["Behavior"]
)


@router.get("/")
def get_behavior(db: Session = Depends(get_db)):
    behavior = get_behavior_features(db)

    return [
        {
            "employee_id": b.employee_id,
            "login_count": b.login_count,
            "unique_pc_count": b.unique_pc_count,
            "weekend_logins": b.weekend_logins,
            "after_hours_logins": b.after_hours_logins,
            "average_login_hour": b.average_login_hour,
        }
        for b in behavior
    ]