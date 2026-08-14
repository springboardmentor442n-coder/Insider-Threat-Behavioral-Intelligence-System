"""
===============================================================================
Service       : New Employee Evaluation Service
File          : backend/services/employee_evaluation_service.py
Project       : Insider Threat Behavioral Intelligence System / SentinelAI

Description   :
    Orchestration layer for evaluating newly submitted employee feature vectors
    against the existing pre-trained 7-model ML pipeline and CERT Layer 2
    behavioral verification.

    Evaluated employees are stored in an in-memory session cache with:
        source = "NEW_EVALUATION"

    The CERT R4.2 population (source = "CERT_R4.2") is NEVER modified.
    datasets/, models/, scripts/, notebooks/ are NEVER written to.
    The population baseline used for CERT Layer 2 is always derived from the
    original CERT dataset, never from the evaluation store.

    This service does NOT retrain models or create a new scaler.
===============================================================================
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from backend.services.live_threat_analyzer_service import analyze_live_employee_threat
from backend.services.verification_service import (
    _load_and_merge_datasets,
    _compute_population_baselines,
    _calculate_percentile,
    _safe_float,
)

logger = logging.getLogger(__name__)

# =============================================================================
# In-Memory Evaluation Store (Session-Scoped)
#
# CRITICAL: This list is NEVER merged with, or used as input for,
# the CERT population baseline calculations.
# =============================================================================

_evaluation_store: List[Dict[str, Any]] = []


# =============================================================================
# Threat Status Determination
# =============================================================================

def determine_threat_status(
    risk_score: float,
    models_triggered: int,
    layer2_supported: bool,
) -> str:
    """
    Derives a scientifically accurate threat status label.

    Uses authoritative risk boundaries:
        HIGH/CRITICAL (>=50) + strong consensus or behavioral support -> POTENTIAL INSIDER THREAT
        Moderate risk or notable model flagging                        -> REQUIRES MONITORING
        Otherwise                                                       -> LOW RISK

    NEVER returns speculative or accusatory labels:
    - No "Confirmed Attacker"
    - No "Confirmed Malicious Employee"
    - No "Guilty" determination
    """
    if risk_score >= 75.0 and (models_triggered >= 5 or layer2_supported):
        return "POTENTIAL INSIDER THREAT"
    if risk_score >= 50.0 or (models_triggered >= 4 and layer2_supported):
        return "POTENTIAL INSIDER THREAT"
    if risk_score >= 25.0 or models_triggered >= 3:
        return "REQUIRES MONITORING"
    return "LOW RISK"


# =============================================================================
# Evaluate + Store
# =============================================================================

def evaluate_employee(
    employee_id: str,
    raw_features: Dict[str, Any],
    employee_name: Optional[str] = None,
    department: Optional[str] = None,
    role: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Runs the full ML inference pipeline on a single employee feature vector.
    Returns the full analysis result WITHOUT storing it.

    Raises:
        ValueError: If features are invalid or missing.
    """
    emp_id = str(employee_id or "NEW-001").strip().upper()

    result = analyze_live_employee_threat(
        employee_id=emp_id,
        raw_features=raw_features,
        employee_name=employee_name,
        department=department,
        role=role,
    )

    # Derive threat status from result
    models_triggered = result.get("models_triggered", 0)
    layer2_supported = bool(
        result.get("layer2_verification", {}).get("supported_by_behavioral_evidence", False)
    )
    risk_score = float(result.get("risk_score", 0.0))

    result["threat_status"] = determine_threat_status(risk_score, models_triggered, layer2_supported)
    result["source"] = "NEW_EVALUATION"

    return result


def save_evaluation(analysis_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Stamps the evaluation with source='NEW_EVALUATION' and evaluation_timestamp,
    then appends it to the in-memory evaluation store.

    If an evaluation with the same employee_id already exists, it is replaced.

    The CERT dataset and CERT population baseline are NEVER modified.
    """
    emp_id = str(
        analysis_result.get("employee", {}).get("employee_id", "")
        or analysis_result.get("employee_id", "UNKNOWN")
    ).strip().upper()

    if not emp_id:
        raise ValueError("employee_id is required to save an evaluation.")

    # Build the stored record
    record = dict(analysis_result)
    record["source"] = "NEW_EVALUATION"
    record["evaluation_timestamp"] = datetime.now(timezone.utc).isoformat()

    # Employee info normalisation
    if "employee" not in record or not isinstance(record["employee"], dict):
        record["employee"] = {}
    record["employee"]["employee_id"] = emp_id

    # Replace if same employee_id already saved in this session
    global _evaluation_store
    _evaluation_store = [e for e in _evaluation_store if _get_emp_id(e) != emp_id]
    _evaluation_store.append(record)

    logger.info(f"[EvaluationStore] Saved NEW_EVALUATION for employee_id={emp_id}")
    return record


def evaluate_and_store(
    employee_id: str,
    raw_features: Dict[str, Any],
    employee_name: Optional[str] = None,
    department: Optional[str] = None,
    role: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Convenience function: evaluate + save in one call.
    """
    result = evaluate_employee(
        employee_id=employee_id,
        raw_features=raw_features,
        employee_name=employee_name,
        department=department,
        role=role,
    )
    return save_evaluation(result)


# =============================================================================
# Retrieval
# =============================================================================

def _get_emp_id(record: Dict[str, Any]) -> str:
    return str(
        record.get("employee", {}).get("employee_id", "")
        or record.get("employee_id", "")
    ).strip().upper()


def get_all_evaluations() -> List[Dict[str, Any]]:
    """
    Returns all saved evaluations sorted by risk_score descending.
    The CERT population is NOT included.
    """
    return sorted(
        _evaluation_store,
        key=lambda r: float(r.get("risk_score", 0.0)),
        reverse=True,
    )


def get_evaluation(employee_id: str) -> Optional[Dict[str, Any]]:
    """
    Returns a single saved evaluation by employee_id, or None if not found.
    """
    target = str(employee_id).strip().upper()
    for record in _evaluation_store:
        if _get_emp_id(record) == target:
            return record
    return None


def delete_evaluation(employee_id: str) -> bool:
    """
    Removes an evaluation from the session store.
    Returns True if deleted, False if not found.
    Administrator-only action enforced at the API layer.
    """
    global _evaluation_store
    target = str(employee_id).strip().upper()
    original_len = len(_evaluation_store)
    _evaluation_store = [e for e in _evaluation_store if _get_emp_id(e) != target]
    deleted = len(_evaluation_store) < original_len
    if deleted:
        logger.info(f"[EvaluationStore] Deleted NEW_EVALUATION record for employee_id={target}")
    return deleted


# =============================================================================
# CERT Population Stats (Read-Only)
# =============================================================================

def _get_cert_risk_scores() -> List[float]:
    """
    Returns all risk scores from the CERT R4.2 population.
    Reads from the immutable parquet. Never modifies the dataset.
    """
    try:
        df = _load_and_merge_datasets()
        col = "weighted_score" if "weighted_score" in df.columns else "risk_score"
        scores = df[col].dropna().tolist()
        return [float(s) for s in scores]
    except Exception as e:
        logger.warning(f"[EvaluationService] Could not load CERT risk scores: {e}")
        return []


def _classify_risk_level(score: float) -> str:
    """
    Maps a 0-100 score to the authoritative 4-tier risk classification.
    """
    if score >= 75.0:
        return "CRITICAL"
    if score >= 50.0:
        return "HIGH"
    if score >= 25.0:
        return "MEDIUM"
    return "LOW"


def _risk_level_counts(scores: List[float]) -> Dict[str, int]:
    counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
    for s in scores:
        lvl = _classify_risk_level(s)
        counts[lvl] += 1
    return counts


# =============================================================================
# Comparison Summary: CERT vs NEW
# =============================================================================

def get_comparison_summary() -> Dict[str, Any]:
    """
    Aggregates statistics for the CERT R4.2 population and the evaluation store.

    CERT stats are always derived from the original, immutable CERT parquet.
    New employees do NOT modify the CERT baseline.
    """
    # ── CERT stats ──────────────────────────────────────────────────────────
    cert_scores = _get_cert_risk_scores()
    cert_total = len(cert_scores)

    if cert_scores:
        cert_avg = round(float(np.mean(cert_scores)), 2)
        cert_median = round(float(np.median(cert_scores)), 2)
        cert_max = round(float(np.max(cert_scores)), 2)
        cert_min = round(float(np.min(cert_scores)), 2)
        cert_p90 = round(float(np.percentile(cert_scores, 90)), 2)
        cert_p95 = round(float(np.percentile(cert_scores, 95)), 2)
    else:
        cert_avg = cert_median = cert_max = cert_min = cert_p90 = cert_p95 = 0.0

    cert_risk_counts = _risk_level_counts(cert_scores)

    # CERT consensus & layer2 from loaded dataset
    cert_consensus_avg = 0.0
    cert_layer2_rate = 0.0
    try:
        df = _load_and_merge_datasets()
        if "Consensus_Percentage" in df.columns:
            cert_consensus_avg = round(float(df["Consensus_Percentage"].dropna().mean()), 2)
    except Exception:
        pass

    # ── NEW EVALUATION stats ─────────────────────────────────────────────────
    new_scores = [float(r.get("risk_score", 0.0)) for r in _evaluation_store]
    new_total = len(new_scores)

    if new_scores:
        new_avg = round(float(np.mean(new_scores)), 2)
        new_median = round(float(np.median(new_scores)), 2)
        new_max = round(float(np.max(new_scores)), 2)
        new_min = round(float(np.min(new_scores)), 2)
    else:
        new_avg = new_median = new_max = new_min = 0.0

    new_risk_counts = _risk_level_counts(new_scores)

    new_consensus_values = [
        float(r.get("consensus_percentage", 0.0)) for r in _evaluation_store
    ]
    new_consensus_avg = round(float(np.mean(new_consensus_values)), 2) if new_consensus_values else 0.0

    new_layer2_supported = sum(
        1 for r in _evaluation_store
        if r.get("layer2_verification", {}).get("supported_by_behavioral_evidence", False)
    )
    new_layer2_rate = round((new_layer2_supported / new_total * 100.0), 1) if new_total else 0.0

    new_threat_count = sum(
        1 for r in _evaluation_store
        if r.get("threat_status") == "POTENTIAL INSIDER THREAT"
    )

    return {
        "cert": {
            "total": cert_total,
            "avg_risk_score": cert_avg,
            "median_risk_score": cert_median,
            "max_risk_score": cert_max,
            "min_risk_score": cert_min,
            "p90_risk_score": cert_p90,
            "p95_risk_score": cert_p95,
            "risk_level_counts": cert_risk_counts,
            "avg_consensus_percentage": cert_consensus_avg,
            "layer2_validation_rate": cert_layer2_rate,
            "source": "CERT_R4.2",
        },
        "new": {
            "total": new_total,
            "avg_risk_score": new_avg,
            "median_risk_score": new_median,
            "max_risk_score": new_max,
            "min_risk_score": new_min,
            "risk_level_counts": new_risk_counts,
            "avg_consensus_percentage": new_consensus_avg,
            "layer2_validation_rate": new_layer2_rate,
            "potential_threat_count": new_threat_count,
            "source": "NEW_EVALUATION",
        },
    }


# =============================================================================
# Combined Ranking
# =============================================================================

def get_comparison_ranking() -> List[Dict[str, Any]]:
    """
    Produces a combined risk ranking containing:
      - Top 50 CERT employees by risk_score (source = "CERT_R4.2")
      - ALL new evaluations (source = "NEW_EVALUATION")

    Sorted by risk_score descending, with integer ranks assigned.

    The CERT and NEW populations are never merged ambiguously:
    each record carries an explicit 'source' field.
    """
    combined: List[Dict[str, Any]] = []

    # ── Top 50 CERT employees ────────────────────────────────────────────────
    try:
        df = _load_and_merge_datasets()

        score_col = "weighted_score" if "weighted_score" in df.columns else "risk_score"
        consensus_col = (
            "Consensus_Percentage" if "Consensus_Percentage" in df.columns else "consensus_percentage"
        )
        suspicious_col = "Suspicious_Count" if "Suspicious_Count" in df.columns else None

        df_sorted = df.sort_values(score_col, ascending=False).head(50)

        for _, row in df_sorted.iterrows():
            raw_score = _safe_float(row.get(score_col, 0.0))
            raw_level = str(row.get("risk_level", "Low"))
            # Normalise risk_level to UPPERCASE
            norm_level = raw_level.strip().upper()
            if norm_level not in ("LOW", "MEDIUM", "HIGH", "CRITICAL"):
                norm_level = _classify_risk_level(raw_score)

            consensus = _safe_float(row.get(consensus_col, 0.0)) if consensus_col else 0.0
            suspicious_count = int(_safe_float(row.get(suspicious_col, 0.0))) if suspicious_col else 0

            layer2_status = "N/A"

            combined.append({
                "employee_id": str(row.get("user", row.get("user_id", ""))),
                "employee_name": str(row.get("employee_name", row.get("user", ""))),
                "source": "CERT_R4.2",
                "risk_score": round(raw_score, 1),
                "risk_level": norm_level,
                "models_triggered": suspicious_count,
                "consensus_percentage": round(consensus, 1),
                "layer2_status": layer2_status,
                "threat_status": determine_threat_status(
                    raw_score, suspicious_count, False
                ),
            })
    except Exception as e:
        logger.warning(f"[EvaluationService] Could not load CERT ranking: {e}")

    # ── All NEW_EVALUATION records ────────────────────────────────────────────
    for record in _evaluation_store:
        emp_info = record.get("employee", {})
        layer2 = record.get("layer2_verification", {})
        layer2_status = (
            "Behaviorally Supported"
            if layer2.get("supported_by_behavioral_evidence")
            else "Lacks Behavioral Support"
        )
        risk_score = float(record.get("risk_score", 0.0))

        combined.append({
            "employee_id": _get_emp_id(record),
            "employee_name": emp_info.get("employee_name", _get_emp_id(record)),
            "source": "NEW_EVALUATION",
            "risk_score": round(risk_score, 1),
            "risk_level": str(record.get("risk_level", _classify_risk_level(risk_score))).upper(),
            "models_triggered": int(record.get("models_triggered", 0)),
            "consensus_percentage": round(float(record.get("consensus_percentage", 0.0)), 1),
            "layer2_status": layer2_status,
            "threat_status": record.get("threat_status", "LOW RISK"),
            "evaluation_timestamp": record.get("evaluation_timestamp", ""),
        })

    # ── Merge + sort + rank ───────────────────────────────────────────────────
    combined.sort(key=lambda r: float(r.get("risk_score", 0.0)), reverse=True)

    for idx, record in enumerate(combined, start=1):
        record["rank"] = idx

    return combined


# =============================================================================
# Individual Percentile Comparison
# =============================================================================

def get_individual_comparison(employee_id: str) -> Dict[str, Any]:
    """
    For a single NEW_EVALUATION employee, computes their percentile rank
    within the CERT R4.2 population across all 6 behavioral dimensions.

    The employee is NOT added to the CERT baseline.
    The CERT dataset is NOT modified.

    Returns per-dimension: employee_value, cert_median, cert_p90, cert_p95,
                           percentile, anomalous
    """
    target = str(employee_id).strip().upper()
    record = get_evaluation(target)

    if record is None:
        raise ValueError(f"No evaluation found for employee_id='{employee_id}'")

    features = record.get("raw_features", {})
    if not features:
        raise ValueError(f"Evaluation for '{employee_id}' has no raw_features stored.")

    # Load CERT population baseline (immutable)
    df = _load_and_merge_datasets()
    baselines = _compute_population_baselines(df)

    # ── Compute employee values for each of the 6 behavioral dimensions ──────
    def fv(key: str) -> float:
        return float(features.get(key, 0.0))

    temporal_val = fv("after_hours_activity") + fv("midnight_activity") + fv("weekend_activity")
    device_val = fv("device_events") + fv("file_events")
    pc_val = fv("unique_pcs")
    web_val = fv("web_events")
    email_val = fv("emails_sent")
    volume_val = fv("total_events")

    def _dim_stats(series: pd.Series, emp_val: float, dim_name: str) -> Dict[str, Any]:
        series_clean = series.dropna()
        if series_clean.empty:
            return {
                "dimension": dim_name,
                "employee_value": round(emp_val, 1),
                "cert_median": 0.0,
                "cert_p90": 0.0,
                "cert_p95": 0.0,
                "percentile": 0.0,
                "anomalous": False,
            }
        cert_median = round(float(series_clean.median()), 2)
        cert_p90 = round(float(np.percentile(series_clean, 90)), 2)
        cert_p95 = round(float(np.percentile(series_clean, 95)), 2)
        pct = round(_calculate_percentile(series_clean, emp_val), 1)
        anomalous = emp_val >= cert_p90 and emp_val > 0
        return {
            "dimension": dim_name,
            "employee_value": round(emp_val, 2),
            "cert_median": cert_median,
            "cert_p90": cert_p90,
            "cert_p95": cert_p95,
            "percentile": pct,
            "anomalous": anomalous,
        }

    dimensions = [
        _dim_stats(baselines["pop_offhours"], temporal_val, "Temporal Activity"),
        _dim_stats(baselines["pop_device"], device_val, "Device / USB Activity"),
        _dim_stats(baselines["pop_pcs"], pc_val, "Multi-PC Access"),
        _dim_stats(baselines["pop_web"], web_val, "Web Activity"),
        _dim_stats(baselines["pop_email"], email_val, "Email Activity"),
        _dim_stats(baselines["pop_events"], volume_val, "Overall Behavioral Volume"),
    ]

    # ── Risk score percentile in CERT population ─────────────────────────────
    cert_risk_scores = _get_cert_risk_scores()
    emp_risk = float(record.get("risk_score", 0.0))
    if cert_risk_scores:
        cert_risk_series = pd.Series(cert_risk_scores)
        risk_pct = round(_calculate_percentile(cert_risk_series, emp_risk), 1)
        cert_risk_median = round(float(np.median(cert_risk_scores)), 2)
        cert_risk_p90 = round(float(np.percentile(cert_risk_scores, 90)), 2)
        cert_risk_p95 = round(float(np.percentile(cert_risk_scores, 95)), 2)
    else:
        risk_pct = 0.0
        cert_risk_median = cert_risk_p90 = cert_risk_p95 = 0.0

    emp_info = record.get("employee", {})

    return {
        "employee_id": target,
        "employee_name": emp_info.get("employee_name", target),
        "department": emp_info.get("department", ""),
        "role": emp_info.get("role", ""),
        "source": "NEW_EVALUATION",
        "risk_score": emp_risk,
        "risk_level": str(record.get("risk_level", _classify_risk_level(emp_risk))).upper(),
        "threat_status": record.get("threat_status", "LOW RISK"),
        "cert_population": {
            "total_employees": len(cert_risk_scores),
            "risk_median": cert_risk_median,
            "risk_p90": cert_risk_p90,
            "risk_p95": cert_risk_p95,
        },
        "employee_risk_percentile": risk_pct,
        "behavioral_dimensions": dimensions,
        "layer2_verification": record.get("layer2_verification", {}),
        "evaluation_timestamp": record.get("evaluation_timestamp", ""),
    }
