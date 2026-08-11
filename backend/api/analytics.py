from fastapi import APIRouter
from fastapi import Depends

from backend.utils.roles import require_roles

from fastapi.responses import FileResponse

from backend.services.export_service import (
    create_analytics_zip,
)

from backend.services.analytics_service import (
    get_model_performance,
    get_training_times,
    get_feature_statistics,
    get_risk_statistics,
    get_dataset_statistics,

    get_dashboard_summary,
    get_department_statistics,
    get_monthly_trends,
    get_risk_distribution,
)

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


# =============================================================================
# Model Performance
# =============================================================================
@router.get("/model-performance")
def model_performance(
    current_user=Depends(
        require_roles(
            "admin",
            "analyst",
        )
    ),
):
    return get_model_performance()


# =============================================================================
# Training Times
# =============================================================================
@router.get("/training-times")
def training_times(
    current_user=Depends(
        require_roles(
            "admin",
            "analyst",
        )
    ),
):
    return get_training_times()


# =============================================================================
# Feature Statistics
# =============================================================================
@router.get("/feature-statistics")
def feature_statistics(
    current_user=Depends(
        require_roles(
            "admin",
            "analyst",
        )
    ),
):
    return get_feature_statistics()


# =============================================================================
# Risk Statistics
# =============================================================================
@router.get("/risk-statistics")
def risk_statistics(
    current_user=Depends(
        require_roles(
            "admin",
            "analyst",
        )
    ),
):
    return get_risk_statistics()


# =============================================================================
# Dataset Statistics
# =============================================================================
@router.get("/dataset-statistics")
def dataset_statistics(
    current_user=Depends(
        require_roles(
            "admin",
            "analyst",
        )
    ),
):
    return get_dataset_statistics()

# =============================================================================
# Analytics Dashboard Summary
# =============================================================================

@router.get("/dashboard")
def analytics_dashboard(
    current_user=Depends(
        require_roles(
            "admin",
            "analyst",
        )
    ),
):
    return get_dashboard_summary()


# =============================================================================
# Department Analytics
# =============================================================================

@router.get("/departments")
def department_analytics(
    current_user=Depends(
        require_roles(
            "admin",
            "analyst",
        )
    ),
):
    return get_department_statistics()


# =============================================================================
# Monthly Trends
# =============================================================================

@router.get("/monthly-trends")
def monthly_trends(
    current_user=Depends(
        require_roles(
            "admin",
            "analyst",
        )
    ),
):
    return get_monthly_trends()


# =============================================================================
# Risk Distribution
# =============================================================================

@router.get("/risk-distribution")
def risk_distribution(
    current_user=Depends(
        require_roles(
            "admin",
            "analyst",
        )
    ),
):
    return get_risk_distribution()


# =============================================================================
# Export Analytics Reports
# =============================================================================

@router.get(
    "/export",
    response_class=FileResponse,
)
def export_analytics(
    current_user=Depends(
        require_roles(
            "admin",
            "analyst",
        )
    ),
):
    zip_file = create_analytics_zip()

    return FileResponse(
        path=zip_file,
        filename="Analytics_Report.zip",
        media_type="application/zip",
    )
