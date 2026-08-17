"""UEBA engine: behavioural baselines, deviation analysis and risk scoring.

The composite risk score blends two independent signals:

  1. A *weighted behavioural score* — how far today's activity sits above the
     user's own historical baseline on the five indicators that matter most
     for insider threat, each carrying the weight defined in RISK_WEIGHTS.
  2. The *ML probability* from the trained Gradient Boosting classifier.

Both land on 0-100 and are combined with the UEBA_WEIGHT / ML_WEIGHT split.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from config import Config
from app.ml.features import BEHAVIOURAL_COLUMNS, FEATURE_LABELS

# Deviation (in baseline std units) at which an indicator is considered
# fully "maxed out" and contributes its entire weight.
SATURATION_SIGMA = 3.0

# Floor on the baseline std so a user who has literally never touched a USB
# stick does not register an infinite z-score the first time they do.
MIN_SIGMA = {
    "files_copied_to_usb": 1.5,
    "off_hours_usb": 0.5,
    "external_emails_sent": 1.0,
    "off_hours_logons": 0.75,
    "cloud_job_visits": 1.0,
}
DEFAULT_MIN_SIGMA = 1.0


def build_baselines(df: pd.DataFrame) -> pd.DataFrame:
    """Per-user historical mean/std for every behavioural feature.

    Returns a frame indexed by user with columns `<feature>_mean` /
    `<feature>_std`, plus the number of observed days.
    """
    grouped = df.groupby("user")[BEHAVIOURAL_COLUMNS]
    means = grouped.mean().add_suffix("_mean")
    stds = grouped.std().fillna(0.0).add_suffix("_std")
    counts = df.groupby("user").size().rename("observed_days")
    return pd.concat([means, stds, counts], axis=1)


def population_means(df: pd.DataFrame) -> pd.Series:
    return df[BEHAVIOURAL_COLUMNS].mean()


def _sigma(user_std: float, feature: str) -> float:
    return max(float(user_std), MIN_SIGMA.get(feature, DEFAULT_MIN_SIGMA))


def deviation_report(
    row: pd.Series, baselines: pd.DataFrame, pop_means: pd.Series
) -> list[dict]:
    """Compare one user-day against that user's baseline, feature by feature."""
    user = row["user"]
    has_baseline = user in baselines.index
    base = baselines.loc[user] if has_baseline else None

    report = []
    for feat in BEHAVIOURAL_COLUMNS:
        observed = float(row.get(feat, 0) or 0)
        if has_baseline:
            mean = float(base.get(f"{feat}_mean", 0.0))
            std = float(base.get(f"{feat}_std", 0.0))
        else:
            # Cold-start: fall back to the population baseline.
            mean = float(pop_means.get(feat, 0.0))
            std = 0.0
        sigma = _sigma(std, feat)
        z = (observed - mean) / sigma
        report.append(
            {
                "feature": feat,
                "label": FEATURE_LABELS.get(feat, feat),
                "observed": round(observed, 2),
                "baseline": round(mean, 2),
                "std": round(sigma, 2),
                "deviation_sigma": round(z, 2),
                "pct_change": (
                    round((observed - mean) / mean * 100, 1) if mean > 0 else None
                ),
                "weighted": feat in Config.RISK_WEIGHTS,
                "weight": Config.RISK_WEIGHTS.get(feat, 0.0),
                "anomalous": bool(z >= 1.5 and observed > mean),
            }
        )
    report.sort(key=lambda d: d["deviation_sigma"], reverse=True)
    return report


def _weighted_matrix(
    df: pd.DataFrame, baselines: pd.DataFrame
) -> tuple[np.ndarray, list[str]]:
    """Vectorised 0-1 saturating deviation per weighted indicator."""
    feats = list(Config.RISK_WEIGHTS)
    aligned = baselines.reindex(df["user"].to_numpy())

    cols = []
    for feat in feats:
        observed = df[feat].to_numpy(dtype=float)
        mean_col = f"{feat}_mean"
        std_col = f"{feat}_std"
        mean = (
            aligned[mean_col].to_numpy(dtype=float)
            if mean_col in aligned.columns
            else np.zeros(len(df))
        )
        std = (
            aligned[std_col].to_numpy(dtype=float)
            if std_col in aligned.columns
            else np.zeros(len(df))
        )
        mean = np.nan_to_num(mean)
        std = np.nan_to_num(std)
        sigma = np.maximum(std, MIN_SIGMA.get(feat, DEFAULT_MIN_SIGMA))
        z = (observed - mean) / sigma
        cols.append(np.clip(z / SATURATION_SIGMA, 0.0, 1.0))
    return np.column_stack(cols), feats


def behavioural_score(df: pd.DataFrame, baselines: pd.DataFrame) -> np.ndarray:
    """Weighted UEBA score in 0-100 for every row of `df`."""
    matrix, feats = _weighted_matrix(df, baselines)
    weights = np.array([Config.RISK_WEIGHTS[f] for f in feats], dtype=float)
    return (matrix @ weights) / weights.sum() * 100.0


def risk_contributions(row: pd.Series, baselines: pd.DataFrame) -> list[dict]:
    """Per-indicator breakdown of the weighted score, for the UI."""
    frame = row.to_frame().T
    matrix, feats = _weighted_matrix(frame, baselines)
    weights = np.array([Config.RISK_WEIGHTS[f] for f in feats], dtype=float)
    total_w = weights.sum()
    out = []
    for i, feat in enumerate(feats):
        share = matrix[0, i] * weights[i] / total_w * 100.0
        out.append(
            {
                "feature": feat,
                "label": FEATURE_LABELS.get(feat, feat),
                "weight": float(weights[i]),
                "intensity": round(float(matrix[0, i]), 3),
                "points": round(float(share), 2),
            }
        )
    out.sort(key=lambda d: d["points"], reverse=True)
    return out


def composite_score(ueba: np.ndarray, ml_prob: np.ndarray) -> np.ndarray:
    score = Config.UEBA_WEIGHT * ueba + Config.ML_WEIGHT * (np.asarray(ml_prob) * 100.0)
    return np.clip(score, 0.0, 100.0)


def severity(score: float) -> str:
    for threshold, name in Config.SEVERITY_THRESHOLDS:
        if score >= threshold:
            return name
    return "LOW"


def severity_series(scores: np.ndarray) -> np.ndarray:
    out = np.full(len(scores), "LOW", dtype=object)
    for threshold, name in sorted(Config.SEVERITY_THRESHOLDS):
        out[np.asarray(scores) >= threshold] = name
    return out
