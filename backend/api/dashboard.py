from fastapi import APIRouter, Depends

from backend.utils.roles import require_roles

from backend.services.dashboard_service import (
    get_dashboard_summary,
    get_risk_distribution,
    get_model_comparison,
    get_system_statistics,
    get_top_suspicious,
)

router = APIRouter()


# =============================================================================
# Dashboard Summary
# =============================================================================
@router.get("/summary")
def dashboard_summary(
    current_user=Depends(
        require_roles(
            "admin",
            "analyst",
            "viewer"
        )
    ),
):
    return get_dashboard_summary()


# =============================================================================
# Risk Distribution
# =============================================================================
@router.get("/risk-distribution")
def risk_distribution(
    current_user=Depends(
        require_roles(
            "admin",
            "analyst",
            "viewer"
        )
    ),
):
    return get_risk_distribution()


# =============================================================================
# Model Comparison
# =============================================================================
@router.get("/model-comparison")
def model_comparison(
    current_user=Depends(
        require_roles(
            "admin",
            "analyst"
        )
    ),
):
    return get_model_comparison()


# =============================================================================
# System Statistics
# =============================================================================
@router.get("/system-statistics")
def system_statistics(
    current_user=Depends(
        require_roles(
            "admin"
        )
    ),
):
    return get_system_statistics()


# =============================================================================
# Top Suspicious Employees
# =============================================================================
@router.get("/top-suspicious")
def top_suspicious(
    current_user=Depends(
        require_roles(
            "admin",
            "analyst",
            "viewer"
        )
    ),
):
    return get_top_suspicious()
