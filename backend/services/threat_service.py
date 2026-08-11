"""
Business logic for Threat Center.

Threat Center GET data is derived from the existing
CERT Insider Threat R4.2 ML employee intelligence.

The existing SQL threat CRUD operations are preserved
for compatibility with the current application architecture.
"""

from sqlalchemy.orm import Session

from backend.crud.threat import (
    get_threats,
    get_threat,
    create_threat,
    update_threat,
    delete_threat,
    resolve_threat,
)

from backend.schemas.threat import (
    ThreatCreate,
    ThreatUpdate,
)

from backend.services.employee_service import (
    get_all_employee_intelligence_service,
    get_employee_intelligence_service,
)


# ============================================================
# ML MODEL DEFINITIONS
# ============================================================

MODEL_COLUMNS = [
    (
        "isolation_forest_prediction",
        "Isolation Forest",
    ),
    (
        "one_class_svm_prediction",
        "One-Class SVM",
    ),
    (
        "lof_prediction",
        "LOF",
    ),
    (
        "elliptic_envelope_prediction",
        "Elliptic Envelope",
    ),
    (
        "pca_prediction",
        "PCA",
    ),
    (
        "dbscan_prediction",
        "DBSCAN",
    ),
    (
        "kmeans_prediction",
        "K-Means",
    ),
]


# ============================================================
# SAFE CONVERSION HELPERS
# ============================================================

def _safe_float(value, default=0.0):
    """
    Safely convert a value to float.
    """

    try:
        if value is None:
            return default

        return float(value)

    except (TypeError, ValueError):
        return default


def _safe_int(value, default=0):
    """
    Safely convert a value to int.
    """

    try:
        if value is None:
            return default

        return int(float(value))

    except (TypeError, ValueError):
        return default


# ============================================================
# BUILD THREAT RECORD
# ============================================================

def _build_threat_record(record: dict) -> dict:
    """
    Convert an existing ML employee intelligence record
    into the shape expected by the Threat Center frontend.

    This does NOT create a database threat.

    It is only an API representation of the existing
    CERT Insider Threat ML result.
    """

    user = str(
        record.get("user") or "Unknown"
    )

    risk_score = _safe_float(
        record.get("risk_score"),
        0.0,
    )

    risk_level = str(
        record.get("risk_level") or "Low"
    )

    rank = _safe_int(
        record.get("rank"),
        0,
    )

    suspicious_count = _safe_int(
        record.get("suspicious_count"),
        0,
    )

    consensus_percentage = _safe_float(
        record.get("consensus_percentage"),
        0.0,
    )

    weighted_score = _safe_float(
        record.get("weighted_score"),
        0.0,
    )

    # --------------------------------------------------------
    # Detect which ML models flagged the employee
    # --------------------------------------------------------

    suspicious_models = []

    for column, model_name in MODEL_COLUMNS:

        prediction = str(
            record.get(column) or ""
        ).strip().lower()

        if prediction == "suspicious":
            suspicious_models.append(model_name)

    if suspicious_models:

        models_triggered = ", ".join(
            suspicious_models
        )

    else:

        models_triggered = "No models flagged"

    # --------------------------------------------------------
    # Threat type
    # --------------------------------------------------------

    if risk_level == "Critical":

        threat_type = (
            "Critical Behavioral Anomaly"
        )

    elif risk_level == "High":

        threat_type = (
            "High-Risk Behavioral Anomaly"
        )

    elif risk_level == "Medium":

        threat_type = (
            "Medium-Risk Behavioral Anomaly"
        )

    else:

        threat_type = "Behavioral Risk"

    # --------------------------------------------------------
    # Description
    # --------------------------------------------------------

    description = (
        f"ML behavioral analysis classified "
        f"{user} as {risk_level} risk with a "
        f"risk score of {risk_score:.2f}. "
        f"{suspicious_count} of 7 anomaly detection "
        f"models flagged suspicious behavior."
    )

    # --------------------------------------------------------
    # Evidence
    # --------------------------------------------------------

    evidence = (
        f"Model consensus: "
        f"{consensus_percentage:.2f}% | "
        f"Weighted score: "
        f"{weighted_score:.2f} | "
        f"Suspicious models: "
        f"{models_triggered}"
    )

    # --------------------------------------------------------
    # Final Threat Center record
    # --------------------------------------------------------

    return {

        # Stable identifier based on ML ranking.
        "id": rank,

        # Existing frontend compatibility fields.
        "employee_id": rank,
        "employee_name": user,
        "department": "CERT Dataset",

        "risk_score": risk_score,
        "severity": risk_level,

        "status": "Open",

        "threat_type": threat_type,

        "description": description,

        "evidence": evidence,

        "models_triggered": models_triggered,

        # ----------------------------------------------------
        # ML-specific information
        # ----------------------------------------------------

        "user": user,

        "risk_level": risk_level,

        "rank": rank,

        "suspicious_count": suspicious_count,

        "consensus_percentage": (
            consensus_percentage
        ),

        "weighted_score": weighted_score,

        # ----------------------------------------------------
        # Isolation Forest
        # ----------------------------------------------------

        "isolation_forest_prediction": (
            record.get(
                "isolation_forest_prediction"
            )
        ),

        "isolation_forest_score": (
            record.get(
                "isolation_forest_score"
            )
        ),

        # ----------------------------------------------------
        # One-Class SVM
        # ----------------------------------------------------

        "one_class_svm_prediction": (
            record.get(
                "one_class_svm_prediction"
            )
        ),

        "one_class_svm_score": (
            record.get(
                "one_class_svm_score"
            )
        ),

        # ----------------------------------------------------
        # LOF
        # ----------------------------------------------------

        "lof_prediction": (
            record.get(
                "lof_prediction"
            )
        ),

        "lof_score": (
            record.get(
                "lof_score"
            )
        ),

        # ----------------------------------------------------
        # Elliptic Envelope
        # ----------------------------------------------------

        "elliptic_envelope_prediction": (
            record.get(
                "elliptic_envelope_prediction"
            )
        ),

        "elliptic_envelope_score": (
            record.get(
                "elliptic_envelope_score"
            )
        ),

        # ----------------------------------------------------
        # PCA
        # ----------------------------------------------------

        "pca_prediction": (
            record.get(
                "pca_prediction"
            )
        ),

        "pca_score": (
            record.get(
                "pca_score"
            )
        ),

        # ----------------------------------------------------
        # DBSCAN
        # ----------------------------------------------------

        "dbscan_prediction": (
            record.get(
                "dbscan_prediction"
            )
        ),

        "dbscan_score": (
            record.get(
                "dbscan_score"
            )
        ),

        # ----------------------------------------------------
        # K-Means
        # ----------------------------------------------------

        "kmeans_prediction": (
            record.get(
                "kmeans_prediction"
            )
        ),

        "kmeans_score": (
            record.get(
                "kmeans_score"
            )
        ),

        # ----------------------------------------------------
        # ML report does not contain a threat event timestamp.
        # ----------------------------------------------------

        "created_at": None,
    }


# ============================================================
# GET ALL THREATS
# ============================================================

def get_all_threats(
    db: Session | None = None,
):
    """
    Return ML-derived risky employees for Threat Center.

    Data source:

        CERT Insider Threat R4.2
        employee_final_risk_report.parquet

    Low-risk employees are excluded because Threat Center
    focuses on detected suspicious behavior.

    The database session parameter is retained for compatibility
    with the existing architecture.
    """

    records = (
        get_all_employee_intelligence_service()
    )

    if not records:
        return []

    threats = []

    for record in records:

        risk_level = str(
            record.get("risk_level") or "Low"
        )

        # ----------------------------------------------------
        # Threat Center only shows Medium / High / Critical
        # ----------------------------------------------------

        if risk_level == "Low":
            continue

        threats.append(
            _build_threat_record(record)
        )

    # --------------------------------------------------------
    # Highest risk first
    # --------------------------------------------------------

    threats.sort(
        key=lambda item: (
            -_safe_float(
                item.get("risk_score"),
                0.0,
            ),
            _safe_int(
                item.get("rank"),
                999999,
            ),
        )
    )

    return threats


# ============================================================
# GET THREAT BY ID
# ============================================================

def get_threat_by_id(
    db: Session | None,
    threat_id: int,
):
    """
    Return one ML-derived Threat Center record.

    The identifier corresponds to the ML employee rank.
    """

    records = (
        get_all_employee_intelligence_service()
    )

    if not records:
        return None

    for record in records:

        rank = _safe_int(
            record.get("rank"),
            0,
        )

        if rank != int(threat_id):
            continue

        risk_level = str(
            record.get("risk_level") or "Low"
        )

        if risk_level == "Low":
            return None

        return _build_threat_record(record)

    return None


# ============================================================
# GET THREAT BY CERT USER
# ============================================================

def get_threat_by_user(
    user: str,
):
    """
    Return one ML Threat Center record by CERT user ID.

    Example:

        AJF0370
        BAL0044
        EIS0041
    """

    record = (
        get_employee_intelligence_service(
            user
        )
    )

    if not record:
        return None

    risk_level = str(
        record.get("risk_level") or "Low"
    )

    if risk_level == "Low":
        return None

    return _build_threat_record(record)


# ============================================================
# CREATE THREAT
# ============================================================

def create_new_threat(
    db: Session,
    threat: ThreatCreate,
):
    """
    Preserve the existing database-backed
    threat creation API.
    """

    return create_threat(
        db,
        threat,
    )


# ============================================================
# UPDATE THREAT
# ============================================================

def update_existing_threat(
    db: Session,
    threat_id: int,
    threat: ThreatUpdate,
):
    """
    Preserve the existing database-backed
    threat update API.
    """

    return update_threat(
        db,
        threat_id,
        threat,
    )


# ============================================================
# DELETE THREAT
# ============================================================

def delete_existing_threat(
    db: Session,
    threat_id: int,
):
    """
    Preserve the existing database-backed
    threat deletion API.
    """

    return delete_threat(
        db,
        threat_id,
    )


# ============================================================
# RESOLVE THREAT
# ============================================================

def resolve_existing_threat(
    db: Session,
    threat_id: int,
):
    """
    Preserve the existing database-backed
    threat resolution API.
    """

    return resolve_threat(
        db,
        threat_id,
    )
