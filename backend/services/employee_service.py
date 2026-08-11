"""
Employee Service

Business logic for:

1. Database-backed Employee CRUD operations.
2. CERT Insider Threat ML employee intelligence.

The existing CRUD functionality is preserved.

ML intelligence is read from the already-generated
employee_final_risk_report.parquet file.
"""

from typing import Any

import pandas as pd
from sqlalchemy.orm import Session

from backend.database.session import SessionLocal

from backend.repositories.employee_repository import (
    create_employee,
    get_all_employees,
    get_employee_by_email,
    get_employee_by_id,
    update_employee,
    delete_employee,
)

from backend.data.parquet_loader import REPORTS


# ============================================================
# Database CRUD
# ============================================================

def create_employee_service(employee_data: dict):
    """
    Create a normal application employee in the database.
    """

    db: Session = SessionLocal()

    try:
        existing = get_employee_by_email(
            db,
            employee_data["email"],
        )

        if existing:
            return None

        return create_employee(
            db,
            employee_data,
        )

    finally:
        db.close()


def get_employee(employee_id: int):
    """
    Get one database-backed employee by database ID.
    """

    db: Session = SessionLocal()

    try:
        return get_employee_by_id(
            db,
            employee_id,
        )

    finally:
        db.close()


def get_all_employees_service():
    """
    Get all database-backed employees.

    This function intentionally remains unchanged in behavior
    so existing CRUD functionality is not broken.
    """

    db: Session = SessionLocal()

    try:
        return get_all_employees(db)

    finally:
        db.close()


def update_employee_service(
    employee_id: int,
    updates: dict,
):
    """
    Update a database-backed employee.
    """

    db: Session = SessionLocal()

    try:

        employee = get_employee_by_id(
            db,
            employee_id,
        )

        if employee is None:
            return None

        return update_employee(
            db,
            employee,
            updates,
        )

    finally:
        db.close()


def delete_employee_service(employee_id: int):
    """
    Delete a database-backed employee.
    """

    db: Session = SessionLocal()

    try:

        employee = get_employee_by_id(
            db,
            employee_id,
        )

        if employee is None:
            return False

        delete_employee(
            db,
            employee,
        )

        return True

    finally:
        db.close()


# ============================================================
# ML Employee Intelligence
# ============================================================

def _safe_value(value: Any, default: Any = 0):
    """
    Convert pandas values into normal Python values.

    This prevents NaN / numpy scalar values from leaking
    into FastAPI responses.
    """

    if pd.isna(value):
        return default

    if hasattr(value, "item"):
        try:
            return value.item()
        except (ValueError, TypeError):
            pass

    return value


def _load_employee_risk_report() -> pd.DataFrame:
    """
    Load the final ML employee risk report.

    Source:
        datasets/exports/employee_final_risk_report.parquet

    This is the final output of the existing ML pipeline.
    """

    if not REPORTS.exists():
        raise FileNotFoundError(
            f"Employee risk report not found: {REPORTS}"
        )

    df = pd.read_parquet(REPORTS)

    if df.empty:
        return df

    required_columns = [
        "user",
        "Isolation Forest_Prediction",
        "Isolation Forest_Score",
        "One-Class SVM_Prediction",
        "One-Class SVM_Score",
        "LOF_Prediction",
        "LOF_Score",
        "Elliptic Envelope_Prediction",
        "Elliptic Envelope_Score",
        "PCA_Prediction",
        "PCA_Score",
        "DBSCAN_Prediction",
        "DBSCAN_Score",
        "KMeans_Prediction",
        "KMeans_Score",
        "Suspicious_Count",
        "Consensus_Percentage",
        "weighted_score",
        "risk_level",
        "Rank",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Employee risk report is missing required columns: "
            + ", ".join(missing_columns)
        )

    return df


def _build_employee_intelligence_record(
    row: pd.Series,
) -> dict:
    """
    Convert one Parquet row into the API response format.
    """

    weighted_score = float(
        _safe_value(
            row["weighted_score"],
            0.0,
        )
    )

    risk_level = str(
        _safe_value(
            row["risk_level"],
            "Low",
        )
    )

    return {
        "user": str(
            _safe_value(
                row["user"],
                "",
            )
        ),

        # Final ML risk score.
        "risk_score": weighted_score,

        "risk_level": risk_level,

        "rank": int(
            _safe_value(
                row["Rank"],
                0,
            )
        ),

        "suspicious_count": int(
            _safe_value(
                row["Suspicious_Count"],
                0,
            )
        ),

        "consensus_percentage": float(
            _safe_value(
                row["Consensus_Percentage"],
                0.0,
            )
        ),

        "weighted_score": weighted_score,

        # ====================================================
        # Isolation Forest
        # ====================================================

        "isolation_forest_prediction": str(
            _safe_value(
                row["Isolation Forest_Prediction"],
                "Normal",
            )
        ),

        "isolation_forest_score": float(
            _safe_value(
                row["Isolation Forest_Score"],
                0.0,
            )
        ),

        # ====================================================
        # One-Class SVM
        # ====================================================

        "one_class_svm_prediction": str(
            _safe_value(
                row["One-Class SVM_Prediction"],
                "Normal",
            )
        ),

        "one_class_svm_score": float(
            _safe_value(
                row["One-Class SVM_Score"],
                0.0,
            )
        ),

        # ====================================================
        # LOF
        # ====================================================

        "lof_prediction": str(
            _safe_value(
                row["LOF_Prediction"],
                "Normal",
            )
        ),

        "lof_score": float(
            _safe_value(
                row["LOF_Score"],
                0.0,
            )
        ),

        # ====================================================
        # Elliptic Envelope
        # ====================================================

        "elliptic_envelope_prediction": str(
            _safe_value(
                row["Elliptic Envelope_Prediction"],
                "Normal",
            )
        ),

        "elliptic_envelope_score": float(
            _safe_value(
                row["Elliptic Envelope_Score"],
                0.0,
            )
        ),

        # ====================================================
        # PCA
        # ====================================================

        "pca_prediction": str(
            _safe_value(
                row["PCA_Prediction"],
                "Normal",
            )
        ),

        "pca_score": float(
            _safe_value(
                row["PCA_Score"],
                0.0,
            )
        ),

        # ====================================================
        # DBSCAN
        # ====================================================

        "dbscan_prediction": str(
            _safe_value(
                row["DBSCAN_Prediction"],
                "Normal",
            )
        ),

        "dbscan_score": float(
            _safe_value(
                row["DBSCAN_Score"],
                0.0,
            )
        ),

        # ====================================================
        # K-Means
        # ====================================================

        "kmeans_prediction": str(
            _safe_value(
                row["KMeans_Prediction"],
                "Normal",
            )
        ),

        "kmeans_score": float(
            _safe_value(
                row["KMeans_Score"],
                0.0,
            )
        ),
    }


def get_all_employee_intelligence_service():
    """
    Return all 1000 employees from the final ML risk report.

    The returned data represents CERT behavioral intelligence,
    not manually-created database employee records.
    """

    df = _load_employee_risk_report()

    if df.empty:
        return []

    records = [
        _build_employee_intelligence_record(row)
        for _, row in df.iterrows()
    ]

    return records


def get_employee_intelligence_service(user: str):
    """
    Return ML intelligence for one CERT user.
    """

    df = _load_employee_risk_report()

    if df.empty:
        return None

    matches = df[
        df["user"].astype(str).str.upper()
        == str(user).upper()
    ]

    if matches.empty:
        return None

    return _build_employee_intelligence_record(
        matches.iloc[0]
    )


def get_employee_intelligence_summary_service():
    """
    Return basic statistics calculated directly from the
    final ML risk report.
    """

    df = _load_employee_risk_report()

    if df.empty:
        return {
            "totalEmployees": 0,
            "averageRisk": 0.0,
            "highestRisk": 0.0,
            "lowestRisk": 0.0,
        }

    scores = pd.to_numeric(
        df["weighted_score"],
        errors="coerce",
    ).dropna()

    if scores.empty:
        return {
            "totalEmployees": len(df),
            "averageRisk": 0.0,
            "highestRisk": 0.0,
            "lowestRisk": 0.0,
        }

    return {
        "totalEmployees": int(len(df)),
        "averageRisk": round(
            float(scores.mean()),
            2,
        ),
        "highestRisk": round(
            float(scores.max()),
            2,
        ),
        "lowestRisk": round(
            float(scores.min()),
            2,
        ),
    }
