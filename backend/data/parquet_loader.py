"""
Centralized Dataset Loader
"""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1].parent

DATASET_ROOT = PROJECT_ROOT / "datasets"


TIMELINE = (
    DATASET_ROOT
    / "integrated"
    / "employee_event_timeline.parquet"
)

FEATURES = (
    DATASET_ROOT
    / "features"
    / "employee_risk_scores.parquet"
)

PREDICTIONS = (
    DATASET_ROOT
    / "predictions"
    / "all_model_predictions.parquet"
)

REPORTS = (
    DATASET_ROOT
    / "exports"
    / "employee_final_risk_report.parquet"
)


def datasets():

    return {

        "timeline": TIMELINE,

        "features": FEATURES,

        "predictions": PREDICTIONS,

        "reports": REPORTS,

    }
