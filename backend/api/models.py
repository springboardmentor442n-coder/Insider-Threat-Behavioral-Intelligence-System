from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from backend.utils.roles import require_roles

from backend.services.model_service import (
    get_model_comparison,
    get_model_performance,
    get_model_ranking,
    get_model_statistics,
    get_model,
    get_model_summary,
)


# =============================================================================
# Router
# =============================================================================

router = APIRouter(
    prefix="/models",
    tags=["Models"],
)


# =============================================================================
# Model Summary
# =============================================================================

@router.get("/summary")
def model_summary(
    current_user=Depends(
        require_roles(
            "admin",
            "analyst",
        )
    ),
):
    """
    Return a summary of all trained models.
    """

    return get_model_summary()


# =============================================================================
# Model Comparison
# =============================================================================

@router.get("/comparison")
def model_comparison(
    current_user=Depends(
        require_roles(
            "admin",
            "analyst",
        )
    ),
):
    """
    Return model comparison results.
    """

    return get_model_comparison()


# =============================================================================
# Model Performance
# =============================================================================

@router.get("/performance")
def model_performance(
    current_user=Depends(
        require_roles(
            "admin",
            "analyst",
        )
    ),
):
    """
    Return model performance metrics.
    """

    return get_model_performance()


# =============================================================================
# Model Ranking
# =============================================================================

@router.get("/ranking")
def model_ranking(
    current_user=Depends(
        require_roles(
            "admin",
            "analyst",
        )
    ),
):
    """
    Return model rankings.
    """

    return get_model_ranking()


# =============================================================================
# Model Statistics
# =============================================================================

@router.get("/statistics")
def model_statistics(
    current_user=Depends(
        require_roles(
            "admin",
            "analyst",
        )
    ),
):
    """
    Return statistical information for model scores.
    """

    return get_model_statistics()


# =============================================================================
# Single Model
# =============================================================================

@router.get("/{model_name}")
def single_model(
    model_name: str,
    current_user=Depends(
        require_roles(
            "admin",
            "analyst",
        )
    ),
):
    """
    Return performance information for a specific model.
    """

    model = get_model(model_name)

    if model is None:

        raise HTTPException(
            status_code=404,
            detail="Model not found.",
        )

    return model
