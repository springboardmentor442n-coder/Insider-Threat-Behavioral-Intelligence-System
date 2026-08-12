from fastapi import APIRouter, Depends, HTTPException
from backend.utils.roles import require_roles

from backend.services.activity_service import (
    get_activity_summary,
    get_activity,
    get_employee_activity,
    get_activity_types,
    get_activity_statistics,
    get_activity_timeline,
)

router = APIRouter(
    prefix="/activity",
    tags=["Activity"],
)

@router.get("/summary")
def summary(
    current_user=Depends(require_roles("admin", "analyst", "viewer")),
):
    return get_activity_summary()

@router.get("/types")
def activity_types(
    current_user=Depends(require_roles("admin", "analyst", "viewer")),
):
    return get_activity_types()

@router.get("/statistics")
def activity_statistics(
    current_user=Depends(require_roles("admin", "analyst", "viewer")),
):
    return get_activity_statistics()

@router.get("/timeline")
def activity_timeline(
    limit: int = 100,
    current_user=Depends(require_roles("admin", "analyst", "viewer")),
):
    return get_activity_timeline(limit=limit)

@router.get("/employee/{employee_id}")
def employee_activity(
    employee_id: str,
    current_user=Depends(require_roles("admin", "analyst", "viewer")),
):
    return get_employee_activity(employee_id)

@router.get("/{activity_type}")
def activity(
    activity_type: str,
    current_user=Depends(require_roles("admin", "analyst", "viewer")),
):
    data = get_activity(activity_type)
    if data is None:
        raise HTTPException(
            status_code=404,
            detail="Activity type not found",
        )
    return data
