from fastapi import APIRouter, Depends

from backend.utils.roles import require_roles

from backend.services.risk_service import (
    calculate_employee_risk,
    get_all_risk_scores,
    get_top_high_risk,
    get_risk_statistics,
)

router = APIRouter()


# ==========================================================
# Get All Risk Scores
# ==========================================================

@router.get("/all")
def all_risks(
    current_user=Depends(
        require_roles(
            "admin",
            "analyst",
            "viewer",
        )
    ),
):
    return get_all_risk_scores()


# ==========================================================
# Top High Risk Employees
# ==========================================================

@router.get("/top")
def top_risk(
    current_user=Depends(
        require_roles(
            "admin",
            "analyst",
            "viewer",
        )
    ),
):
    return get_top_high_risk()


# ==========================================================
# Risk Statistics
# ==========================================================

@router.get("/statistics")
def statistics(
    current_user=Depends(
        require_roles(
            "admin",
            "analyst",
        )
    ),
):
    return get_risk_statistics()


# ==========================================================
# Single Employee Risk
# ==========================================================

@router.get("/{employee_id}")
def employee_risk(
    employee_id: str,
    current_user=Depends(
        require_roles(
            "admin",
            "analyst",
            "viewer",
        )
    ),
):
    return calculate_employee_risk(employee_id)
