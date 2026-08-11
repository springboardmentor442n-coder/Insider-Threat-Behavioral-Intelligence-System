"""
Model Service

Provides access to trained machine learning model
performance, rankings, comparisons, and statistics.
"""

from pathlib import Path

from backend.utils.config import REPORTS_DIR
from backend.utils.data_loader import load_csv


# =============================================================================
# Report Paths
# =============================================================================

MODEL_COMPARISON_FILE = REPORTS_DIR / "model_comparison.csv"
MODEL_PERFORMANCE_FILE = REPORTS_DIR / "model_performance.csv"
MODEL_RANKING_FILE = REPORTS_DIR / "model_ranking.csv"
MODEL_STATISTICS_FILE = REPORTS_DIR / "model_statistics.csv"


# =============================================================================
# Helpers
# =============================================================================

def _load_records(path: Path):
    """
    Safely load a CSV report and return records.
    """

    if not path.exists():
        return []

    df = load_csv(path)

    if df.empty:
        return []

    return df.to_dict(orient="records")


# =============================================================================
# Get Model Comparison
# =============================================================================

def get_model_comparison():
    """
    Return model comparison results.
    """

    return _load_records(MODEL_COMPARISON_FILE)


# =============================================================================
# Get Model Performance
# =============================================================================

def get_model_performance():
    """
    Return model performance results.
    """

    return _load_records(MODEL_PERFORMANCE_FILE)


# =============================================================================
# Get Model Ranking
# =============================================================================

def get_model_ranking():
    """
    Return model ranking results.
    """

    return _load_records(MODEL_RANKING_FILE)


# =============================================================================
# Get Model Statistics
# =============================================================================

def get_model_statistics():
    """
    Return statistical information for model scores.
    """

    records = _load_records(MODEL_STATISTICS_FILE)

    results = []

    for item in records:

        results.append(
            {
                "feature": item.get("Unnamed: 0"),
                "count": item.get("count"),
                "mean": item.get("mean"),
                "std": item.get("std"),
                "min": item.get("min"),
                "25%": item.get("25%"),
                "50%": item.get("50%"),
                "75%": item.get("75%"),
                "max": item.get("max"),
            }
        )

    return results


# =============================================================================
# Get Single Model
# =============================================================================

def get_model(model_name: str):
    """
    Return information for one model.
    """

    models = get_model_performance()

    for model in models:

        if str(model.get("Model", "")).lower() == model_name.lower():

            return model

    return None


# =============================================================================
# Model Summary
# =============================================================================

def get_model_summary():
    """
    Return a compact summary of available models.
    """

    models = get_model_performance()

    if not models:
        return {
            "total_models": 0,
            "best_detection_rate": None,
            "fastest_model": None,
            "most_suspicious": None,
        }

    best_detection = max(
        models,
        key=lambda item: float(
            item.get("Detection Rate (%)", 0) or 0
        ),
    )

    fastest_model = min(
        models,
        key=lambda item: float(
            item.get("Training Time (sec)", 0) or 0
        ),
    )

    most_suspicious = max(
        models,
        key=lambda item: int(
            item.get("Suspicious Employees", 0) or 0
        ),
    )

    return {
        "total_models": len(models),

        "best_detection_rate": {
            "model": best_detection.get("Model"),
            "value": best_detection.get("Detection Rate (%)"),
        },

        "fastest_model": {
            "model": fastest_model.get("Model"),
            "value": fastest_model.get("Training Time (sec)"),
        },

        "most_suspicious": {
            "model": most_suspicious.get("Model"),
            "value": most_suspicious.get("Suspicious Employees"),
        },
    }
