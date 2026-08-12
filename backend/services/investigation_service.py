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
import pandas as pd
from backend.data.parquet_loader import REPORTS


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

from backend.utils.cert_date_helper import get_cert_date_for_user

INVESTIGATION_CASES: list[dict[str, Any]] = [
    {
        "id": "CASE-1001",
        "employee": "John Carter",
        "department": "Finance",
        "risk_score": 96,
        "prediction": "Malicious Insider",
        "status": "Open",
        "assigned_to": "SOC Team",
        "created_at": "2011-05-01",
        "last_updated": "2011-05-15",
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
        "created_at": "2011-05-03",
        "last_updated": "2011-05-16",
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
        "created_at": "2011-04-28",
        "last_updated": "2011-05-10",
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

    assigned = normalized.get("assigned_to")
    if not assigned or str(assigned).strip() == "" or str(assigned).strip() == "None":
        normalized["assigned_to"] = "Unassigned"

    created = normalized.get("created_at") or normalized.get("created")
    if not created:
        created = datetime.now().strftime("%Y-%m-%d")
    normalized["created_at"] = str(created)

    updated = normalized.get("updated_at") or normalized.get("last_updated")
    if not updated:
        updated = str(created)
    normalized["updated_at"] = str(updated)
    normalized["last_updated"] = str(updated)

    return normalized


# ============================================================
# Get all investigation cases
# ============================================================

_ml_cases_initialized = False

def _initialize_ml_cases() -> None:
    """
    Pre-seeds top ML suspicious employees as initial investigation cases
    alongside the existing demonstration cases.
    """
    global _ml_cases_initialized, INVESTIGATION_CASES
    if _ml_cases_initialized:
        return
    _ml_cases_initialized = True

    if not REPORTS.exists():
        return

    try:
        risk_df = pd.read_parquet(REPORTS)
        if risk_df.empty:
            return

        risk_df = risk_df.sort_values(by="weighted_score", ascending=False)
        top_suspicious = risk_df[
            (risk_df["risk_level"].isin(["Critical", "High"])) |
            (risk_df["Suspicious_Count"] >= 3)
        ].head(10)

        existing_ids = set()
        for c in INVESTIGATION_CASES:
            existing_ids.add(str(c.get("employee", "")).upper())
            existing_ids.add(str(c.get("user", "")).upper())
            existing_ids.add(str(c.get("id", "")).upper())

        for _, row in top_suspicious.iterrows():
            user_str = str(row.get("user", "")).strip()
            if not user_str or user_str.upper() in existing_ids:
                continue

            score = float(row.get("weighted_score", 0.0))
            level = str(row.get("risk_level", "Medium"))
            susp_count = int(row.get("Suspicious_Count", 0))
            case_id = f"CASE-{user_str.upper()}"

            if case_id.upper() in existing_ids:
                continue

            user_date = get_cert_date_for_user(user_str, int(row.get("Rank", 1)))
            INVESTIGATION_CASES.append({
                "id": case_id,
                "employee": user_str,
                "user": user_str,
                "employee_id": user_str,
                "department": "CERT Dataset",
                "risk_score": round(score, 1),
                "risk_level": level,
                "prediction": f"Flagged Behavioral Anomaly ({susp_count}/7 Models)",
                "status": "Open" if score >= 80 else "Under Review",
                "assigned_to": "SOC Team",
                "created_at": user_date,
                "last_updated": user_date,
                "evidence": [
                    f"{susp_count}/7 Models Unsupervised Consensus",
                    f"Risk Score {score:.1f}/100 ({level} Risk)",
                    "Anomalous CERT Behavioral Activity"
                ],
                "notes": "Employee flagged by behavioral intelligence system and submitted for analyst investigation."
            })
            existing_ids.add(user_str.upper())
            existing_ids.add(case_id.upper())
    except Exception:
        pass


def create_or_get_investigation(employee_id: str) -> dict[str, Any]:
    """
    Creates an investigation case for an employee if one does not already exist.
    If a case already exists, returns the existing case (Duplicate Protection).
    """
    _initialize_ml_cases()
    clean_id = str(employee_id).strip().upper()

    for case in INVESTIGATION_CASES:
        c_emp = str(case.get("employee", "")).strip().upper()
        c_usr = str(case.get("user", "")).strip().upper()
        c_id = str(case.get("id", "")).strip().upper()
        if clean_id in [c_emp, c_usr, c_id] or c_id == f"CASE-{clean_id}":
            return _normalize_case(case)

    score = 80.0
    level = "High"
    susp_count = 3

    if REPORTS.exists():
        try:
            risk_df = pd.read_parquet(REPORTS)
            matches = risk_df[risk_df["user"].astype(str).str.upper() == clean_id]
            if not matches.empty:
                r = matches.iloc[0]
                score = float(r.get("weighted_score", 80.0))
                level = str(r.get("risk_level", "High"))
                susp_count = int(r.get("Suspicious_Count", 3))
        except Exception:
            pass

    case_id = f"CASE-{clean_id}"
    user_date = get_cert_date_for_user(clean_id)
    new_case = {
        "id": case_id,
        "employee": clean_id,
        "user": clean_id,
        "employee_id": clean_id,
        "department": "CERT Dataset",
        "risk_score": round(score, 1),
        "risk_level": level,
        "prediction": f"Flagged Behavioral Anomaly ({susp_count}/7 Models)",
        "status": "Open",
        "assigned_to": "SOC Team",
        "created_at": user_date,
        "last_updated": user_date,
        "evidence": [
            f"{susp_count}/7 Models Unsupervised Consensus",
            f"Risk Score {score:.1f}/100 ({level} Risk)",
            "Submitted for analyst investigation"
        ],
        "notes": "Employee flagged by behavioral intelligence system and submitted for analyst investigation."
    }

    INVESTIGATION_CASES.append(new_case)
    return _normalize_case(new_case)


def get_all_cases() -> list[dict[str, Any]]:
    """
    Return all investigation cases.
    """
    _initialize_ml_cases()
    return [
        _normalize_case(case)
        for case in INVESTIGATION_CASES
    ]


def get_case(case_id: str) -> dict[str, Any] | None:
    """
    Return one investigation case by case ID or employee ID.
    """
    _initialize_ml_cases()
    clean_id = str(case_id).strip().upper()

    for case in INVESTIGATION_CASES:
        c_emp = str(case.get("employee", "")).strip().upper()
        c_usr = str(case.get("user", "")).strip().upper()
        c_id = str(case.get("id", "")).strip().upper()
        if clean_id in [c_emp, c_usr, c_id] or c_id == f"CASE-{clean_id}":
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

    now_str = datetime.now().strftime("%Y-%m-%d")
    case["status"] = status
    case["last_updated"] = now_str
    case["updated_at"] = now_str

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

    now_str = datetime.now().strftime("%Y-%m-%d")
    case["assigned_to"] = analyst
    case["last_updated"] = now_str
    case["updated_at"] = now_str

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
    now_str = datetime.now().strftime("%Y-%m-%d")
    case["last_updated"] = now_str
    case["updated_at"] = now_str

    return _normalize_case(case)


SEVERITY_ORDER = ["Informational", "Low", "Medium", "High", "Critical"]


def escalate_case(
    case_id: str,
    username: str = "Analyst",
) -> dict[str, Any] | None:
    """
    Escalate case severity by one level (up to Critical) and log escalation metadata.
    """
    case = next(
        (item for item in INVESTIGATION_CASES if item["id"] == case_id),
        None,
    )

    if case is None:
        return None

    curr_lvl = case.get("risk_level", "Medium")
    if curr_lvl in SEVERITY_ORDER:
        idx = SEVERITY_ORDER.index(curr_lvl)
        if idx < len(SEVERITY_ORDER) - 1:
            case["risk_level"] = SEVERITY_ORDER[idx + 1]

    case["status"] = "Escalated"
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date_str = datetime.now().strftime("%Y-%m-%d")
    case["escalated_at"] = now_str
    case["escalated_by"] = username
    case["last_updated"] = date_str
    case["updated_at"] = date_str

    return _normalize_case(case)
