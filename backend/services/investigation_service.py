"""
Investigation Service

Provides investigation cases for the Insider Threat Behavioral
Intelligence System.

The investigation layer uses the application's canonical risk
representation:

    risk_score : 0 - 100

Risk levels follow the same thresholds used by the ML risk-scoring
pipeline:

    0  - <30  : Low
    30 - <60  : Medium
    60 - <80  : High
    80 - 100  : Critical

NOTE:
The existing investigation workflow currently uses a small set of
static demonstration cases. These cases are retained so that the
Investigation UI continues to function without changing the existing
API contract.

The important correction here is that risk levels are derived from
the canonical thresholds instead of maintaining a second set of
inconsistent thresholds.
"""

from datetime import datetime
from typing import Any


# ============================================================
# Risk-level helper
# ============================================================

def get_risk_level(risk_score: float) -> str:
    """
    Convert a canonical 0-100 risk score into the project's
    standard risk level.

    Thresholds MUST remain synchronized with:

        scripts/data_engineering/09_risk_scoring.py
    """

    try:
        score = float(risk_score)
    except (TypeError, ValueError):
        score = 0.0

    # Protect the application from invalid values.
    score = max(0.0, min(100.0, score))

    if score >= 80:
        return "Critical"

    if score >= 60:
        return "High"

    if score >= 30:
        return "Medium"

    return "Low"


# ============================================================
# Static investigation cases
# ============================================================
#
# These are the existing demonstration cases.
#
# IMPORTANT:
# We intentionally preserve the existing case IDs, names,
# evidence, statuses, assignments, and dates so that the
# existing frontend does not break.
#
# Risk level is generated from risk_score instead of being
# independently hardcoded.
# ============================================================

INVESTIGATION_CASES: list[dict[str, Any]] = [
    {
        "id": "CASE-1001",
        "employee": "John Carter",
        "department": "Finance",
        "risk_score": 96,
        "prediction": "Malicious Insider",
        "status": "Open",
        "assigned_to": "SOC Team",
        "created_at": "2026-08-01",
        "last_updated": "2026-08-08",
        "evidence": [
            "USB Device Activity",
            "Large File Transfer",
            "After Hours Login",
        ],
        "notes": "High confidence anomaly detected.",
    },
    {
        "id": "CASE-1002",
        "employee": "Sarah Lee",
        "department": "HR",
        "risk_score": 82,
        "prediction": "Suspicious",
        "status": "Under Review",
        "assigned_to": "Analyst",
        "created_at": "2026-08-03",
        "last_updated": "2026-08-08",
        "evidence": [
            "Email Spike",
            "Multiple Failed Logins",
        ],
        "notes": "Behaviour requires manual review.",
    },
    {
        "id": "CASE-1003",
        "employee": "Michael Brown",
        "department": "IT",
        "risk_score": 71,
        "prediction": "Medium Risk",
        "status": "Closed",
        "assigned_to": "SOC Team",
        "created_at": "2026-07-28",
        "last_updated": "2026-08-05",
        "evidence": [
            "VPN Login",
        ],
        "notes": "False positive confirmed.",
    },
]


# ============================================================
# Normalize investigation case
# ============================================================

def _normalize_case(case: dict[str, Any]) -> dict[str, Any]:
    """
    Return a normalized investigation case.

    This guarantees that every case exposes:

        risk_score
        risk_level

using the same 0-100 risk convention used throughout the
application.
    """

    normalized = dict(case)

    try:
        score = float(normalized.get("risk_score", 0))
    except (TypeError, ValueError):
        score = 0.0

    score = max(0.0, min(100.0, score))

    normalized["risk_score"] = round(score, 2)
    normalized["risk_level"] = get_risk_level(score)

    return normalized


# ============================================================
# Get all investigation cases
# ============================================================

def get_all_cases() -> list[dict[str, Any]]:
    """
    Return all investigation cases.

    A normalized copy is returned so callers cannot accidentally
    modify the internal case collection through this function.
    """

    return [
        _normalize_case(case)
        for case in INVESTIGATION_CASES
    ]


# ============================================================
# Get single investigation case
# ============================================================

def get_case(case_id: str) -> dict[str, Any] | None:
    """
    Return one investigation case by case ID.
    """

    for case in INVESTIGATION_CASES:
        if case["id"] == case_id:
            return _normalize_case(case)

    return None


# ============================================================
# Update investigation status
# ============================================================

def update_case_status(
    case_id: str,
    status: str,
) -> dict[str, Any] | None:
    """
    Update the status of an investigation case.
    """

    case = next(
        (
            item
            for item in INVESTIGATION_CASES
            if item["id"] == case_id
        ),
        None,
    )

    if case is None:
        return None

    case["status"] = status
    case["last_updated"] = datetime.now().strftime(
        "%Y-%m-%d"
    )

    return _normalize_case(case)


# ============================================================
# Assign investigation case
# ============================================================

def assign_case(
    case_id: str,
    analyst: str,
) -> dict[str, Any] | None:
    """
    Assign an investigation case to an analyst/team.
    """

    case = next(
        (
            item
            for item in INVESTIGATION_CASES
            if item["id"] == case_id
        ),
        None,
    )

    if case is None:
        return None

    case["assigned_to"] = analyst
    case["last_updated"] = datetime.now().strftime(
        "%Y-%m-%d"
    )

    return _normalize_case(case)


# ============================================================
# Add investigation note
# ============================================================

def add_note(
    case_id: str,
    note: str,
) -> dict[str, Any] | None:
    """
    Append an analyst note to an investigation case.
    """

    case = next(
        (
            item
            for item in INVESTIGATION_CASES
            if item["id"] == case_id
        ),
        None,
    )

    if case is None:
        return None

    clean_note = str(note).strip()

    if clean_note:
        existing_notes = str(
            case.get("notes", "")
        ).strip()

        if existing_notes:
            case["notes"] = (
                f"{existing_notes}\n{clean_note}"
            )
        else:
            case["notes"] = clean_note

    case["last_updated"] = datetime.now().strftime(
        "%Y-%m-%d"
    )

    return _normalize_case(case)
