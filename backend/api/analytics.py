from fastapi import APIRouter
from fastapi import Depends

from backend.utils.roles import require_roles

from backend.services.analytics_service import (
    get_model_performance,
    get_training_times,
    get_feature_statistics,
    get_risk_statistics,
    get_dataset_statistics,
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
