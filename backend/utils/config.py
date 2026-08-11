"""Centralized report and artifact paths.

This module keeps the existing import surface used by backend services while
delegating all runtime path resolution to the centralized settings layer.
"""

from backend.settings import settings

# =============================================================================
# Project Directories
# =============================================================================

PROJECT_ROOT = settings.project_root

REPORTS_DIR = settings.reports_dir
MODELS_DIR = settings.models_dir
PLOTS_DIR = settings.plots_dir

# =============================================================================
# Dashboard Reports
# =============================================================================

TOP_SUSPICIOUS = REPORTS_DIR / "top_suspicious.csv"
TOP_100_SUSPICIOUS = REPORTS_DIR / "top_100_suspicious.csv"

CRITICAL_EMPLOYEE_SUMMARY = REPORTS_DIR / "critical_employee_summary.csv"

MODEL_COMPARISON = REPORTS_DIR / "model_comparison.csv"

PERFORMANCE_METRICS = REPORTS_DIR / "performance_metrics.csv"

SYSTEM_STATISTICS = REPORTS_DIR / "system_statistics.csv"

RISK_LEVEL_DISTRIBUTION = REPORTS_DIR / "risk_level_distribution.csv"

# =============================================================================
# Analytics Reports
# =============================================================================

MODEL_PERFORMANCE = REPORTS_DIR / "model_performance.csv"

TRAINING_TIMES = REPORTS_DIR / "training_times.csv"

FEATURE_STATISTICS = REPORTS_DIR / "feature_statistics.csv"

RISK_LEVEL_STATISTICS = REPORTS_DIR / "risk_level_statistics.csv"

DATASET_STATISTICS = REPORTS_DIR / "dataset_statistics.csv"

FEATURE_IMPORTANCE = REPORTS_DIR / "feature_importance.csv"

# =============================================================================
# Explainability Reports (For Phase 12.5)
# =============================================================================

EMPLOYEE_EXPLANATIONS = REPORTS_DIR / "employee_explanations.csv"

TOP_BEHAVIORAL_FACTORS = REPORTS_DIR / "top_behavioral_factors.csv"

# =============================================================================
# Report Downloads (For Phase 12.6)
# =============================================================================

CONSENSUS_SUMMARY = REPORTS_DIR / "consensus_summary.csv"

MODEL_RANKING = REPORTS_DIR / "model_ranking.csv"

TRAINING_TIME_RANKING = REPORTS_DIR / "training_time_ranking.csv"

CLASSIFICATION_REPORT = REPORTS_DIR / "classification_report.csv"

# =============================================================================
# All Report Files
# =============================================================================

REPORT_FILES = {
    "top_suspicious": TOP_SUSPICIOUS,
    "top_100_suspicious": TOP_100_SUSPICIOUS,
    "critical_employee_summary": CRITICAL_EMPLOYEE_SUMMARY,
    "model_comparison": MODEL_COMPARISON,
    "model_performance": MODEL_PERFORMANCE,
    "performance_metrics": PERFORMANCE_METRICS,
    "system_statistics": SYSTEM_STATISTICS,
    "risk_level_distribution": RISK_LEVEL_DISTRIBUTION,
    "risk_level_statistics": RISK_LEVEL_STATISTICS,
    "dataset_statistics": DATASET_STATISTICS,
    "feature_statistics": FEATURE_STATISTICS,
    "feature_importance": FEATURE_IMPORTANCE,
    "employee_explanations": EMPLOYEE_EXPLANATIONS,
    "top_behavioral_factors": TOP_BEHAVIORAL_FACTORS,
    "consensus_summary": CONSENSUS_SUMMARY,
    "model_ranking": MODEL_RANKING,
    "training_times": TRAINING_TIMES,
    "training_time_ranking": TRAINING_TIME_RANKING,
    "classification_report": CLASSIFICATION_REPORT,
}
