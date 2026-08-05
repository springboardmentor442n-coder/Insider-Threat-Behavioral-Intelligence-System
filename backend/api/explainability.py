from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from backend.utils.roles import require_roles

from backend.services.explainability_service import (
    get_employee_explanation,
    get_feature_importance,
    get_top_behavioral_factors,
)

router = APIRouter()


# =============================================================================
# Feature Importance
# =============================================================================

@router.get("/feature-importance")
def feature_importance(
    current_user=Depends(
        require_roles(
            "admin",
            "analyst",
            "viewer",
        )
    ),
):
    return get_feature_importance()


# =============================================================================
# Top Behavioral Factors
# =============================================================================

@router.get("/top-behavioral-factors")
def top_behavioral_factors(
    current_user=Depends(
        require_roles(
            "admin",
            "analyst",
            "viewer",
        )
    ),
):
    return get_top_behavioral_factors()


# =============================================================================
# Employee Explanation
# =============================================================================

@router.get("/{employee_id}")
def employee_explanation(
    employee_id: str,
    current_user=Depends(
        require_roles(
            "admin",
            "analyst",
            "viewer",
        )
    ),
):

    data = get_employee_explanation(employee_id)

    if data is None:
        raise HTTPException(
            status_code=404,
            detail="Employee explanation not found.",
        )

    return data
