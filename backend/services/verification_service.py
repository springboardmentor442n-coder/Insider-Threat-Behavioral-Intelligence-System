"""
===============================================================================
Service       : CERT Behavioral Pattern Validation Service
File          : backend/services/verification_service.py
Project       : Insider Threat Behavioral Intelligence System

Description   :
    Evaluates ML-detected suspicious users against population-level
    baselines across CERT R4.2 behavioral anomaly dimensions.

    Uses statistical thresholding (percentiles, population medians/means)
    to confirm whether unsupervised model detections are supported by
    statistically anomalous behavioral evidence.

    IMPORTANT:
    This service performs Behavioral Pattern Validation (Layer 2).
    It does NOT perform Ground Truth Classification (Layer 1) because
    official CERT malicious-user labels are not available locally.
===============================================================================
"""

from typing import Dict, List, Any, Optional
from pathlib import Path
import pandas as pd
import numpy as np
import logging

from backend.data.parquet_loader import FEATURES, REPORTS

logger = logging.getLogger(__name__)

DISCLAIMER_TEXT = (
    "Behavioral Pattern Validation is an independent behavioral consistency "
    "check against CERT-documented anomaly dimensions. It is not ground-truth "
    "classification because official CERT malicious-user labels are not "
    "currently available."
)

_cached_merged_df: Optional[pd.DataFrame] = None


def _load_and_merge_datasets() -> pd.DataFrame:
    """
    Loads employee features and employee final risk report,
    merging them on the 'user' column.
    """
    global _cached_merged_df

    if _cached_merged_df is not None:
        return _cached_merged_df

    # Load feature dataset
    emp_features_path = FEATURES.parent / "employee_features.parquet"
    if emp_features_path.exists():
        feature_df = pd.read_parquet(emp_features_path)
    elif FEATURES.exists():
        feature_df = pd.read_parquet(FEATURES)
    else:
        raise FileNotFoundError(f"Feature dataset not found at {emp_features_path}")

    # Load risk report dataset
    if not REPORTS.exists():
        raise FileNotFoundError(f"Risk report dataset not found at {REPORTS}")

    risk_df = pd.read_parquet(REPORTS)

    # Normalize user join key
    if "user" not in feature_df.columns and "user_id" in feature_df.columns:
        feature_df = feature_df.rename(columns={"user_id": "user"})

    if "user" not in risk_df.columns and "user_id" in risk_df.columns:
        risk_df = risk_df.rename(columns={"user_id": "user"})

    # Merge datasets
    merged = pd.merge(
        risk_df,
        feature_df,
        on="user",
        how="inner",
        suffixes=("", "_feat")
    )

    _cached_merged_df = merged
    return _cached_merged_df


def _calculate_percentile(series: pd.Series, value: float) -> float:
    """
    Calculate the percentile rank of a value within a series (0.0 to 100.0).
    """
    if series.empty:
        return 0.0
    return float((series < value).mean() * 100.0)


def _safe_float(val: Any, default: float = 0.0) -> float:
    """
    Safely convert values to float.
    """
    if pd.isna(val):
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def _safe_int(val: Any, default: int = 0) -> int:
    """
    Safely convert values to int.
    """
    if pd.isna(val):
        return default
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return default


def _compute_population_baselines(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Safely computes population baselines once for all 6 CERT behavioral dimensions.
    """
    def _get_series(col_name: str) -> pd.Series:
        val = df.get(col_name, 0)
        if isinstance(val, pd.Series):
            return val.fillna(0)
        return pd.Series([0] * len(df), index=df.index)

    # Vector 1: Temporal
    pop_offhours = (
        _get_series("after_hours_activity")
        + _get_series("midnight_activity")
        + _get_series("weekend_activity")
    )
    p1_clean = pop_offhours.dropna()
    p1_median = _safe_float(p1_clean.median())
    p1_mean = _safe_float(p1_clean.mean())
    p1_p90 = _safe_float(np.percentile(p1_clean, 90)) if not p1_clean.empty else 0.0

    # Vector 2: Device
    pop_device = (
        _get_series("device_events")
        + _get_series("file_events")
    )
    p2_clean = pop_device.dropna()
    p2_median = _safe_float(p2_clean.median())
    p2_mean = _safe_float(p2_clean.mean())
    p2_p90 = _safe_float(np.percentile(p2_clean, 90)) if not p2_clean.empty else 0.0

    # Vector 3: Multi-PC
    pop_pcs = _get_series("unique_pcs")
    p3_clean = pop_pcs.dropna()
    p3_median = _safe_float(p3_clean.median())
    p3_mean = _safe_float(p3_clean.mean())
    p3_p90 = _safe_float(np.percentile(p3_clean, 90)) if not p3_clean.empty else 0.0

    # Vector 4: Web
    pop_web = _get_series("web_events")
    p4_clean = pop_web.dropna()
    p4_median = _safe_float(p4_clean.median())
    p4_mean = _safe_float(p4_clean.mean())
    p4_p90 = _safe_float(np.percentile(p4_clean, 90)) if not p4_clean.empty else 0.0

    # Vector 5: Email
    pop_email = _get_series("emails_sent")
    p5_clean = pop_email.dropna()
    p5_median = _safe_float(p5_clean.median())
    p5_mean = _safe_float(p5_clean.mean())
    p5_p90 = _safe_float(np.percentile(p5_clean, 90)) if not p5_clean.empty else 0.0

    # Vector 6: Overall Volume
    pop_events = _get_series("total_events")
    p6_clean = pop_events.dropna()
    p6_median = _safe_float(p6_clean.median())
    p6_mean = _safe_float(p6_clean.mean())
    p6_p90 = _safe_float(np.percentile(p6_clean, 90)) if not p6_clean.empty else 0.0

    return {
        "pop_offhours": pop_offhours, "p1_median": p1_median, "p1_mean": p1_mean, "p1_p90": p1_p90,
        "pop_device": pop_device, "p2_median": p2_median, "p2_mean": p2_mean, "p2_p90": p2_p90,
        "pop_pcs": pop_pcs, "p3_median": p3_median, "p3_mean": p3_mean, "p3_p90": p3_p90,
        "pop_web": pop_web, "p4_median": p4_median, "p4_mean": p4_mean, "p4_p90": p4_p90,
        "pop_email": pop_email, "p5_median": p5_median, "p5_mean": p5_mean, "p5_p90": p5_p90,
        "pop_events": pop_events, "p6_median": p6_median, "p6_mean": p6_mean, "p6_p90": p6_p90,
    }


def evaluate_employee_behavioral_vectors(
    row: pd.Series,
    df: pd.DataFrame,
    baselines: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Evaluates an employee's feature row against 6 CERT behavioral dimensions
    using population-level baseline statistics (mean, median, 90th percentile).
    """
    if baselines is None:
        baselines = _compute_population_baselines(df)

    vectors = []

    # -------------------------------------------------------------------------
    # Vector 1: Temporal Activity (Unusual Logon Times & After-Hours Work)
    # -------------------------------------------------------------------------
    after_hours = _safe_float(row.get("after_hours_activity", 0))
    midnight = _safe_float(row.get("midnight_activity", 0))
    weekend = _safe_float(row.get("weekend_activity", 0))
    combined_offhours = after_hours + midnight + weekend

    pop_offhours = baselines["pop_offhours"]
    p_median = baselines["p1_median"]
    p_mean = baselines["p1_mean"]
    p90_offhours = baselines["p1_p90"]
    percentile_offhours = _calculate_percentile(pop_offhours, combined_offhours)

    is_temporal_anomalous = combined_offhours >= p90_offhours and combined_offhours > 50

    vectors.append({
        "vector_id": "temporal",
        "vector_name": "Temporal Activity",
        "cert_dimension": "Unusual Logon Times & After-Hours Work",
        "feature_used": "after_hours + midnight + weekend events",
        "employee_value": _safe_int(combined_offhours),
        "population_median": round(p_median, 1),
        "population_mean": round(p_mean, 1),
        "population_p90": round(p90_offhours, 1),
        "percentile": round(percentile_offhours, 1),
        "threshold_used": f"Top 10% of population (>= {round(p90_offhours, 1)} events)",
        "anomalous": is_temporal_anomalous,
        "evidence": (
            f"Employee recorded {int(combined_offhours):,} off-hours/weekend events "
            f"({percentile_offhours:.1f}th percentile), "
            f"{'exceeding' if is_temporal_anomalous else 'within'} the 90th percentile baseline threshold "
            f"({round(p90_offhours, 1):,} events)."
        )
    })

    # -------------------------------------------------------------------------
    # Vector 2: Device & Removable Media (USB Exfiltration Indicators)
    # -------------------------------------------------------------------------
    device_events = _safe_float(row.get("device_events", 0))
    file_events = _safe_float(row.get("file_events", 0))
    unique_files = _safe_float(row.get("unique_files", 0))
    combined_device = device_events + file_events

    pop_device = baselines["pop_device"]
    p_median_dev = baselines["p2_median"]
    p_mean_dev = baselines["p2_mean"]
    p90_device = baselines["p2_p90"]
    percentile_device = _calculate_percentile(pop_device, combined_device)

    is_device_anomalous = combined_device >= p90_device and combined_device > 0

    vectors.append({
        "vector_id": "device",
        "vector_name": "Device & Removable Media",
        "cert_dimension": "Unusual / Increased Removable Media & File Copying",
        "feature_used": "device_events + file_events",
        "employee_value": _safe_int(combined_device),
        "population_median": round(p_median_dev, 1),
        "population_mean": round(p_mean_dev, 1),
        "population_p90": round(p90_device, 1),
        "percentile": round(percentile_device, 1),
        "threshold_used": f"Top 10% of population (>= {round(p90_device, 1)} events)",
        "anomalous": is_device_anomalous,
        "evidence": (
            f"Employee executed {int(device_events):,} USB device connections and "
            f"{int(file_events):,} removable file copies ({int(unique_files):,} unique files), "
            f"ranking in the {percentile_device:.1f}th percentile."
        )
    })

    # -------------------------------------------------------------------------
    # Vector 3: Multi-PC Access (Machine Access Anomalies)
    # -------------------------------------------------------------------------
    unique_pcs = _safe_float(row.get("unique_pcs", 0))
    pop_pcs = baselines["pop_pcs"]
    p_median_pc = baselines["p3_median"]
    p_mean_pc = baselines["p3_mean"]
    p90_pc = baselines["p3_p90"]
    percentile_pc = _calculate_percentile(pop_pcs, unique_pcs)

    is_pc_anomalous = unique_pcs >= p90_pc and unique_pcs > 2

    vectors.append({
        "vector_id": "multi_pc",
        "vector_name": "Multi-PC Access",
        "cert_dimension": "Unusual Logins to Other Dedicated/Shared Machines",
        "feature_used": "unique_pcs",
        "employee_value": _safe_int(unique_pcs),
        "population_median": round(p_median_pc, 1),
        "population_mean": round(p_mean_pc, 1),
        "population_p90": round(p90_pc, 1),
        "percentile": round(percentile_pc, 1),
        "threshold_used": f"Top 10% of population (>= {round(p90_pc, 1)} PCs)",
        "anomalous": is_pc_anomalous,
        "evidence": (
            f"Employee logged into {int(unique_pcs):,} distinct PCs enterprise-wide "
            f"({percentile_pc:.1f}th percentile), vs. population median of {round(p_median_pc, 1)} PC."
        )
    })

    # -------------------------------------------------------------------------
    # Vector 4: Web Activity (Web Browsing Volume & Diversity)
    # -------------------------------------------------------------------------
    web_events = _safe_float(row.get("web_events", 0))
    unique_urls = _safe_float(row.get("unique_urls", 0))
    pop_web = baselines["pop_web"]
    p_median_web = baselines["p4_median"]
    p_mean_web = baselines["p4_mean"]
    p90_web = baselines["p4_p90"]
    percentile_web = _calculate_percentile(pop_web, web_events)

    is_web_anomalous = web_events >= p90_web and web_events > 500

    vectors.append({
        "vector_id": "web",
        "vector_name": "Web Activity",
        "cert_dimension": "Changes in Web Browsing Volume & URL Diversity",
        "feature_used": "web_events + unique_urls",
        "employee_value": _safe_int(web_events),
        "population_median": round(p_median_web, 1),
        "population_mean": round(p_mean_web, 1),
        "population_p90": round(p90_web, 1),
        "percentile": round(percentile_web, 1),
        "threshold_used": f"Top 10% of population (>= {round(p90_web, 1)} HTTP events)",
        "anomalous": is_web_anomalous,
        "evidence": (
            f"Employee generated {int(web_events):,} web events across {int(unique_urls):,} unique URLs "
            f"({percentile_web:.1f}th percentile), vs. population median of {round(p_median_web, 1):,} events."
        )
    })

    # -------------------------------------------------------------------------
    # Vector 5: Email Activity (Email Transmission Volume)
    # -------------------------------------------------------------------------
    emails_sent = _safe_float(row.get("emails_sent", 0))
    pop_email = baselines["pop_email"]
    p_median_email = baselines["p5_median"]
    p_mean_email = baselines["p5_mean"]
    p90_email = baselines["p5_p90"]
    percentile_email = _calculate_percentile(pop_email, emails_sent)

    is_email_anomalous = emails_sent >= p90_email and emails_sent > 100

    vectors.append({
        "vector_id": "email",
        "vector_name": "Email Activity",
        "cert_dimension": "Number of Emails Sent / Day & Surge Transmission",
        "feature_used": "emails_sent",
        "employee_value": _safe_int(emails_sent),
        "population_median": round(p_median_email, 1),
        "population_mean": round(p_mean_email, 1),
        "population_p90": round(p90_email, 1),
        "percentile": round(percentile_email, 1),
        "threshold_used": f"Top 10% of population (>= {round(p90_email, 1)} emails)",
        "anomalous": is_email_anomalous,
        "evidence": (
            f"Employee transmitted {int(emails_sent):,} emails "
            f"({percentile_email:.1f}th percentile), vs. population median of {round(p_median_email, 1):,} emails."
        )
    })

    # -------------------------------------------------------------------------
    # Vector 6: Overall Behavioral Volume (Spike in Enterprise Activity)
    # -------------------------------------------------------------------------
    total_events = _safe_float(row.get("total_events", 0))
    pop_events = baselines["pop_events"]
    p_median_events = baselines["p6_median"]
    p_mean_events = baselines["p6_mean"]
    p90_events = baselines["p6_p90"]
    percentile_events = _calculate_percentile(pop_events, total_events)

    is_volume_anomalous = total_events >= p90_events

    vectors.append({
        "vector_id": "overall_volume",
        "vector_name": "Overall Behavioral Volume",
        "cert_dimension": "Radical Changes in Behavioral Activity Surge",
        "feature_used": "total_events",
        "employee_value": _safe_int(total_events),
        "population_median": round(p_median_events, 1),
        "population_mean": round(p_mean_events, 1),
        "population_p90": round(p90_events, 1),
        "percentile": round(percentile_events, 1),
        "threshold_used": f"Top 10% of population (>= {round(p90_events, 1)} events)",
        "anomalous": is_volume_anomalous,
        "evidence": (
            f"Employee accumulated {int(total_events):,} total enterprise events "
            f"({percentile_events:.1f}th percentile), vs. population median of {round(p_median_events, 1):,} events."
        )
    })

    return vectors


def get_behavioral_validation_summary() -> Dict[str, Any]:
    """
    Generates population-wide summary of CERT Behavioral Pattern Validation.
    """
    df = _load_and_merge_datasets()
    total_employees = len(df)

    if df.empty:
        return {
            "disclaimer": DISCLAIMER_TEXT,
            "total_employees": 0,
            "suspicious_employees_count": 0,
            "vector_summaries": [],
            "validated_employees": []
        }

    # Evaluate all employees for vector anomalies
    baselines = _compute_population_baselines(df)

    all_evaluated = []
    vector_counts = {
        "temporal": 0,
        "device": 0,
        "multi_pc": 0,
        "web": 0,
        "email": 0,
        "overall_volume": 0
    }

    for _, row in df.iterrows():
        user_id = str(row.get("user", ""))
        weighted_score = _safe_float(row.get("weighted_score", 0.0))
        risk_level = str(row.get("risk_level", "Low"))
        suspicious_count = _safe_int(row.get("Suspicious_Count", 0))
        consensus_pct = _safe_float(row.get("Consensus_Percentage", 0.0))

        vectors = evaluate_employee_behavioral_vectors(row, df, baselines)
        anomalous_vectors = [v for v in vectors if v["anomalous"]]
        flagged_vector_ids = [v["vector_id"] for v in anomalous_vectors]

        for vid in flagged_vector_ids:
            if vid in vector_counts:
                vector_counts[vid] += 1

        is_suspicious = suspicious_count >= 3 or risk_level in ["High", "Critical"]

        item = {
            "user": user_id,
            "employee_id": user_id,
            "risk_score": round(weighted_score, 1),
            "risk_level": risk_level,
            "suspicious_model_count": suspicious_count,
            "consensus_percentage": round(consensus_pct, 1),
            "is_suspicious_ml": is_suspicious,
            "vectors_flagged_count": len(anomalous_vectors),
            "vectors_flagged_names": [v["vector_name"] for v in anomalous_vectors],
            "supported_by_behavioral_evidence": len(anomalous_vectors) >= 2 and is_suspicious,
            "vectors": vectors
        }
        all_evaluated.append(item)

    # Filter ML-suspicious or High/Critical risk employees
    suspicious_employees = [
        emp for emp in all_evaluated
        if emp["is_suspicious_ml"] or emp["risk_level"] in ["High", "Critical", "Medium"]
    ]

    # Sort by risk score descending
    suspicious_employees.sort(key=lambda x: x["risk_score"], reverse=False)
    # Sort descending
    suspicious_employees.sort(key=lambda x: x["risk_score"], reverse=True)

    vector_summaries = [
        {
            "vector_id": "temporal",
            "vector_name": "Temporal Activity",
            "cert_dimension": "Unusual Logon Times & After-Hours Work",
            "anomalous_count": vector_counts["temporal"],
            "percentage": round((vector_counts["temporal"] / total_employees) * 100.0, 1),
            "description": "Logons or enterprise activity occurring during midnight, after-hours, or weekends."
        },
        {
            "vector_id": "device",
            "vector_name": "Device & Removable Media",
            "cert_dimension": "Unusual / Increased Removable Media & File Copying",
            "anomalous_count": vector_counts["device"],
            "percentage": round((vector_counts["device"] / total_employees) * 100.0, 1),
            "description": "USB drive connects and file exfiltration attempts to removable media."
        },
        {
            "vector_id": "multi_pc",
            "vector_name": "Multi-PC Access",
            "cert_dimension": "Unusual Logins to Other Dedicated/Shared Machines",
            "anomalous_count": vector_counts["multi_pc"],
            "percentage": round((vector_counts["multi_pc"] / total_employees) * 100.0, 1),
            "description": "Accessing multiple non-dedicated or lab PCs across the network."
        },
        {
            "vector_id": "web",
            "vector_name": "Web Activity",
            "cert_dimension": "Changes in Web Browsing Volume & URL Diversity",
            "anomalous_count": vector_counts["web"],
            "percentage": round((vector_counts["web"] / total_employees) * 100.0, 1),
            "description": "High volume HTTP requests and expansive web browsing URL counts."
        },
        {
            "vector_id": "email",
            "vector_name": "Email Activity",
            "cert_dimension": "Number of Emails Sent / Day & Surge Transmission",
            "anomalous_count": vector_counts["email"],
            "percentage": round((vector_counts["email"] / total_employees) * 100.0, 1),
            "description": "High volume email transmissions exceeding enterprise norms."
        },
        {
            "vector_id": "overall_volume",
            "vector_name": "Overall Behavioral Volume",
            "cert_dimension": "Radical Changes in Behavioral Activity Surge",
            "anomalous_count": vector_counts["overall_volume"],
            "percentage": round((vector_counts["overall_volume"] / total_employees) * 100.0, 1),
            "description": "Aggregate enterprise activity surge across all combined channels."
        }
    ]

    total_suspicious_count = len([e for e in all_evaluated if e["is_suspicious_ml"]])

    return {
        "disclaimer": DISCLAIMER_TEXT,
        "total_employees": total_employees,
        "suspicious_employees_count": total_suspicious_count,
        "validated_employees_count": len([e for e in suspicious_employees if e["supported_by_behavioral_evidence"]]),
        "vector_summaries": vector_summaries,
        "validated_employees": suspicious_employees
    }


def get_individual_employee_behavioral_validation(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Returns detailed CERT Behavioral Pattern Validation for a specific user ID.
    """
    df = _load_and_merge_datasets()

    user_matches = df[df["user"].astype(str).str.upper() == str(user_id).upper()]
    if user_matches.empty:
        return None

    row = user_matches.iloc[0]

    user_str = str(row.get("user", ""))
    weighted_score = _safe_float(row.get("weighted_score", 0.0))
    risk_level = str(row.get("risk_level", "Low"))
    suspicious_count = _safe_int(row.get("Suspicious_Count", 0))
    consensus_pct = _safe_float(row.get("Consensus_Percentage", 0.0))
    rank = _safe_int(row.get("Rank", 0))

    baselines = _compute_population_baselines(df)
    vectors = evaluate_employee_behavioral_vectors(row, df, baselines)
    anomalous_vectors = [v for v in vectors if v["anomalous"]]

    # Model predictions breakdown
    model_predictions = {}
    for col in row.index:
        if col.endswith("_Prediction"):
            model_name = col.replace("_Prediction", "")
            model_predictions[model_name] = str(row[col])

    return {
        "disclaimer": DISCLAIMER_TEXT,
        "user": user_str,
        "employee_id": user_str,
        "risk_score": round(weighted_score, 1),
        "risk_level": risk_level,
        "rank": rank,
        "suspicious_model_count": suspicious_count,
        "consensus_percentage": round(consensus_pct, 1),
        "supported_by_behavioral_evidence": len(anomalous_vectors) >= 2 and (suspicious_count >= 3 or risk_level in ["High", "Critical"]),
        "anomalous_vector_count": len(anomalous_vectors),
        "total_vectors_tested": len(vectors),
        "model_predictions": model_predictions,
        "behavioral_vectors": vectors
    }
