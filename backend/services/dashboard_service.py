"""
Dashboard Service

Provides dashboard-level data for the Insider Threat Behavioral
Intelligence System.

Canonical API risk-score convention
------------------------------------
All API responses from this service expose:

    risk_score = 0 - 100

The underlying generated reports may contain either:

    0 - 1
or
    0 - 100

This service normalizes both representations into the single
API representation:

    0 - 100

Risk levels:

    0  - <30 : Low
    30 - <60 : Medium
    60 - <80 : High
    80 - 100 : Critical
"""

from __future__ import annotations

import pandas as pd

from backend.services.ldap_service import load_employee_directory

from backend.utils.config import (
    TOP_SUSPICIOUS,
    MODEL_COMPARISON,
    SYSTEM_STATISTICS,
    RISK_LEVEL_DISTRIBUTION,
)

from backend.utils.data_loader import load_csv


# =============================================================================
# Risk Helpers
# =============================================================================

def normalize_risk_score(value) -> float:
    """
    Convert a stored risk score into the application's canonical
    0-100 representation.

    Supported input formats:

        0.72  -> 72.0
        0.85  -> 85.0
        1.00  -> 100.0
        72.0  -> 72.0
        85.0  -> 85.0
        100.0 -> 100.0

    Invalid values become 0.

    IMPORTANT:
    This function exists because the current project contains
    generated reports using both 0-1 and 0-100 representations.
    """

    try:
        score = float(value)
    except (TypeError, ValueError):
        return 0.0

    if pd.isna(score):
        return 0.0

    # -------------------------------------------------------------------------
    # Normalize 0-1 representation to 0-100.
    #
    # Example:
    #
    #     0.72 -> 72
    #     0.85 -> 85
    #
    # Scores exactly equal to 1 are also treated as normalized 100.
    # -------------------------------------------------------------------------

    if 0 <= score <= 1:
        score *= 100

    # -------------------------------------------------------------------------
    # Protect the API from invalid values.
    # -------------------------------------------------------------------------

    score = max(
        0.0,
        min(100.0, score),
    )

    return round(
        score,
        2,
    )


def get_risk_level(score) -> str:
    """
    Convert a canonical 0-100 risk score into the standard
    project risk level.

    These thresholds match:

        scripts/data_engineering/09_risk_scoring.py
    """

    score = normalize_risk_score(score)

    if score >= 80:
        return "Critical"

    if score >= 60:
        return "High"

    if score >= 30:
        return "Medium"

    return "Low"


# =============================================================================
# Dashboard Summary
# =============================================================================

def get_dashboard_summary():
    """
    Return the executive dashboard summary.
    """

    system_df = load_csv(
        SYSTEM_STATISTICS
    )

    risk_df = load_csv(
        RISK_LEVEL_DISTRIBUTION
    )

    model_df = load_csv(
        MODEL_COMPARISON
    )

    summary = {
        "employeesProcessed": 0,
        "criticalEmployees": 0,
        "highRiskEmployees": 0,
        "mediumRiskEmployees": 0,
        "lowRiskEmployees": 0,
        "machineLearningModels": 0,
        "featuresGenerated": 0,
        "reportsGenerated": 0,
        "executionTimeSeconds": 0,
        "bestModel": "",
        "bestModelTrainingTime": 0,
    }

    # =========================================================================
    # System Statistics
    # =========================================================================

    if not system_df.empty:

        stats = dict(
            zip(
                system_df["Metric"],
                system_df["Value"],
            )
        )

        summary["employeesProcessed"] = int(
            stats.get(
                "Employees Processed",
                0,
            )
        )

        summary["machineLearningModels"] = int(
            stats.get(
                "Machine Learning Models",
                0,
            )
        )

        summary["featuresGenerated"] = int(
            stats.get(
                "Features Generated",
                0,
            )
        )

        summary["reportsGenerated"] = int(
            stats.get(
                "Reports Generated",
                0,
            )
        )

        summary["executionTimeSeconds"] = float(
            stats.get(
                "Execution Time (sec)",
                0,
            )
        )

    # =========================================================================
    # Risk Distribution
    # =========================================================================

    if not risk_df.empty:

        for _, row in risk_df.iterrows():

            level = str(
                row.get(
                    "Risk Level",
                    "",
                )
            ).strip()

            try:
                employees = int(
                    float(
                        row.get(
                            "Employees",
                            0,
                        )
                    )
                )
            except (TypeError, ValueError):

                employees = 0

            if level == "Low":

                summary["lowRiskEmployees"] = employees

            elif level == "Medium":

                summary["mediumRiskEmployees"] = employees

            elif level == "High":

                summary["highRiskEmployees"] = employees

            elif level == "Critical":

                summary["criticalEmployees"] = employees

    # =========================================================================
    # Best Model
    # =========================================================================

    if not model_df.empty:

        if "Training Time (sec)" in model_df.columns:

            fastest = model_df.sort_values(
                by="Training Time (sec)",
                ascending=True,
            ).iloc[0]

            summary["bestModel"] = str(
                fastest.get(
                    "Model",
                    "",
                )
            )

            try:
                summary["bestModelTrainingTime"] = float(
                    fastest.get(
                        "Training Time (sec)",
                        0,
                    )
                )
            except (TypeError, ValueError):

                summary["bestModelTrainingTime"] = 0

    return summary


# =============================================================================
# Risk Distribution
# =============================================================================

def get_risk_distribution():
    """
    Return the generated risk-level distribution.
    """

    df = load_csv(
        RISK_LEVEL_DISTRIBUTION
    )

    if df.empty:
        return []

    return df.to_dict(
        orient="records"
    )


# =============================================================================
# Model Comparison
# =============================================================================

def get_model_comparison():
    """
    Return model comparison information.
    """

    df = load_csv(
        MODEL_COMPARISON
    )

    if df.empty:
        return []

    return df.to_dict(
        orient="records"
    )


# =============================================================================
# System Statistics
# =============================================================================

def get_system_statistics():
    """
    Return system statistics.
    """

    df = load_csv(
        SYSTEM_STATISTICS
    )

    if df.empty:
        return []

    return df.to_dict(
        orient="records"
    )


# =============================================================================
# Top Suspicious Employees
# =============================================================================

def get_top_suspicious(limit=20):
    """
    Return the highest-risk employees enriched with LDAP metadata.

    IMPORTANT:
    The API always returns risk_score on a 0-100 scale.

    Therefore:

        stored 0.72 -> API 72.0
        stored 0.85 -> API 85.0
        stored 72   -> API 72.0
        stored 100  -> API 100.0
    """

    # =========================================================================
    # Validate limit
    # =========================================================================

    try:
        limit = int(limit)
    except (TypeError, ValueError):

        limit = 20

    limit = max(
        1,
        min(limit, 1000),
    )

    # =========================================================================
    # Load ML-generated risk data
    # =========================================================================

    suspicious_df = load_csv(
        TOP_SUSPICIOUS
    )

    if suspicious_df.empty:
        return []

    # =========================================================================
    # Resolve Risk Score Column
    # =========================================================================
    #
    # The current ML pipeline exports:
    #
    #     weighted_score
    #
    # while the backend API expects:
    #
    #     risk_score
    #
    # Some generated reports already contain risk_score.
    #
    # Prefer risk_score if available, otherwise use weighted_score.
    # =========================================================================

    if "risk_score" not in suspicious_df.columns:

        if "weighted_score" in suspicious_df.columns:

            suspicious_df["risk_score"] = (
                suspicious_df["weighted_score"]
            )

        else:

            suspicious_df["risk_score"] = 0.0

    # =========================================================================
    # Normalize Risk Scores
    # =========================================================================

    suspicious_df["risk_score"] = (
        suspicious_df["risk_score"]
        .apply(normalize_risk_score)
    )

    # =========================================================================
    # Calculate Canonical Severity
    # =========================================================================

    suspicious_df["severity"] = (
        suspicious_df["risk_score"]
        .apply(get_risk_level)
    )

    # =========================================================================
    # Sort
    # =========================================================================

    suspicious_df = suspicious_df.sort_values(
        by="risk_score",
        ascending=False,
    )

    # =========================================================================
    # Load Employee Directory
    # =========================================================================

    ldap_df = load_employee_directory()

    # =========================================================================
    # LDAP Unavailable
    # =========================================================================

    if ldap_df.empty:

        result = suspicious_df.head(
            limit
        ).copy()

        required_columns = [
            "user",
            "employee_name",
            "department",
            "role",
            "risk_score",
            "severity",
            "prediction",
            "business_unit",
            "functional_unit",
            "team",
            "supervisor",
        ]

        for column in required_columns:

            if column not in result.columns:

                result[column] = None

        result = result[
            required_columns
        ]

        result = result.replace(
            [
                float("inf"),
                float("-inf"),
            ],
            None,
        )

        result = result.where(
            pd.notnull(result),
            None,
        )

        return result.to_dict(
            orient="records"
        )

    # =========================================================================
    # Standardize LDAP Identifier
    # =========================================================================

    if "user_id" in ldap_df.columns:

        ldap_df = ldap_df.rename(
            columns={
                "user_id": "user",
            }
        )

    # =========================================================================
    # LDAP Must Have User Identifier
    # =========================================================================

    if "user" not in ldap_df.columns:

        ldap_df = pd.DataFrame(
            columns=[
                "user",
            ]
        )

    # =========================================================================
    # Prevent Duplicate Employee Rows
    # =========================================================================

    ldap_df = ldap_df.drop_duplicates(
        subset=["user"],
        keep="first",
    )

    # =========================================================================
    # Merge ML Risk Data With LDAP
    # =========================================================================

    merged = suspicious_df.merge(
        ldap_df,
        on="user",
        how="left",
        suffixes=(
            "",
            "_ldap",
        ),
    )

    # =========================================================================
    # Re-normalize After Merge
    # =========================================================================

    merged["risk_score"] = (
        merged["risk_score"]
        .apply(normalize_risk_score)
    )

    # =========================================================================
    # Recalculate Severity
    # =========================================================================

    merged["severity"] = (
        merged["risk_score"]
        .apply(get_risk_level)
    )

    # =========================================================================
    # Sort Highest Risk First
    # =========================================================================

    merged = merged.sort_values(
        by="risk_score",
        ascending=False,
    )

    # =========================================================================
    # Required API Columns
    # =========================================================================

    required_columns = [
        "user",
        "employee_name",
        "department",
        "role",
        "risk_score",
        "severity",
        "prediction",
        "business_unit",
        "functional_unit",
        "team",
        "supervisor",
    ]

    for column in required_columns:

        if column not in merged.columns:

            merged[column] = None

    # =========================================================================
    # Final Response
    # =========================================================================

    result = merged[
        required_columns
    ].head(limit).copy()

    # =========================================================================
    # Remove NaN / Infinity
    # =========================================================================

    result = result.replace(
        [
            float("inf"),
            float("-inf"),
        ],
        None,
    )

    result = result.where(
        pd.notnull(result),
        None,
    )

    return result.to_dict(
        orient="records"
    )
