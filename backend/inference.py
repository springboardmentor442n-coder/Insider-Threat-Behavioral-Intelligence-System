import pandas as pd
import numpy as np
import joblib
import json
from functools import reduce
from pathlib import Path

MODEL_DIR = Path(__file__).parent.parent / "models"


def detect_log_type(df: pd.DataFrame) -> str:
    cols = set(df.columns)
    if "url" in cols:
        return "http"
    if "to" in cols and "attachments" in cols:
        return "email"
    if "filename" in cols:
        return "file"
    if "activity" in cols and "pc" in cols:
        sample = df["activity"].dropna().unique()[:5]
        if any(v in ("Logon", "Logoff") for v in sample):
            return "logon"
        elif any(v in ("Connect", "Disconnect") for v in sample):
            return "device"
    raise ValueError(f"Could not identify log type from columns: {cols}")


def build_daily_features(df: pd.DataFrame, log_type: str) -> pd.DataFrame:
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], format="%m/%d/%Y %H:%M:%S", errors="coerce")
    df["day"] = df["date"].dt.date

    if log_type == "logon":
        df["hour"] = df["date"].dt.hour
        df["dow"] = df["date"].dt.dayofweek
        df["is_logon"] = (df["activity"] == "Logon").astype(int)
        df["is_logoff"] = (df["activity"] == "Logoff").astype(int)
        df["is_after_hours"] = ((df["hour"] < 6) | (df["hour"] > 20)).astype(int)
        df["is_weekend"] = (df["dow"] >= 5).astype(int)
        return df.groupby(["user", "day"]).agg(
            n_logons=("is_logon", "sum"), n_logoffs=("is_logoff", "sum"),
            first_hour=("hour", "min"), last_hour=("hour", "max"),
            after_hours_events=("is_after_hours", "sum"),
            n_pcs=("pc", "nunique"), is_weekend_activity=("is_weekend", "max"),
        ).reset_index()

    elif log_type == "device":
        df["is_connect"] = (df["activity"] == "Connect").astype(int)
        df["is_disconnect"] = (df["activity"] == "Disconnect").astype(int)
        return df.groupby(["user", "day"]).agg(
            n_device_connects=("is_connect", "sum"),
            n_device_disconnects=("is_disconnect", "sum"),
        ).reset_index()

    elif log_type == "email":
        df["n_to"] = df["to"].fillna("").str.count(";") + 1
        df["has_attachment"] = (df["attachments"] > 0).astype(int)
        return df.groupby(["user", "day"]).agg(
            n_emails_sent=("user", "count"), total_recipients=("n_to", "sum"),
            n_emails_with_attachment=("has_attachment", "sum"),
            total_email_size=("size", "sum"),
        ).reset_index()

    elif log_type == "file":
        df["ext"] = df["filename"].str.extract(r"\.(\w+)$")
        return df.groupby(["user", "day"]).agg(
            n_file_copies=("user", "count"), n_distinct_file_types=("ext", "nunique"),
        ).reset_index()

    elif log_type == "http":
        df["domain"] = df["url"].str.extract(r"http://([^/]+)/")
        return df.groupby(["user", "day"]).agg(
            n_http_requests=("user", "count"), n_distinct_domains=("domain", "nunique"),
        ).reset_index()


def predict_from_dataframes(raw_dataframes: list[tuple[pd.DataFrame, str]]) -> pd.DataFrame:
    """raw_dataframes: list of (df, log_type) tuples."""
    model = joblib.load(MODEL_DIR / "isolation_forest.joblib")
    with open(MODEL_DIR / "feature_columns.json") as f:
        feature_cols = json.load(f)
    with open(MODEL_DIR / "normalization_stats.json") as f:
        norm_stats = json.load(f)
    role_stats = pd.read_parquet(MODEL_DIR / "role_stats.parquet")
    ldap_latest = pd.read_parquet(MODEL_DIR / "ldap_latest.parquet")

    daily_frames = [build_daily_features(df, log_type) for df, log_type in raw_dataframes]
    features_df = reduce(lambda l, r: pd.merge(l, r, on=["user", "day"], how="outer"), daily_frames)
    features_df = features_df.fillna(0)

    base_feature_cols = [c for c in features_df.columns if c not in ["user", "day"]]

    for c in [c for c in feature_cols if not (c.endswith("_role_zscore") or c.endswith("_deviation"))]:
        if c not in features_df.columns:
            features_df[c] = 0

    features_df = features_df.merge(ldap_latest, on="user", how="left")

    for c in base_feature_cols:
        mean_col, std_col = (c, "mean"), (c, "std")
        if mean_col in role_stats.columns:
            role_mean_map = role_stats[mean_col].to_dict()
            role_std_map = role_stats[std_col].to_dict()
            features_df[f"{c}_role_zscore"] = features_df.apply(
                lambda r: (r[c] - role_mean_map.get(r["role"], 0)) / (role_std_map.get(r["role"], 1) + 1e-6)
                if pd.notna(r["role"]) else 0, axis=1
            )
        else:
            features_df[f"{c}_role_zscore"] = 0

    rolling_cols = ["n_logons", "after_hours_events", "n_device_connects", "n_emails_sent", "n_file_copies"]
    for c in rolling_cols:
        if f"{c}_deviation" not in features_df.columns:
            features_df[f"{c}_deviation"] = 0

    for c in feature_cols:
        if c not in features_df.columns:
            features_df[c] = 0
    X = features_df[feature_cols].fillna(0).to_numpy()

    anomaly_scores = -model.decision_function(X)
    min_s, max_s = norm_stats["anomaly_score_min"], norm_stats["anomaly_score_max"]
    risk_score = np.clip((anomaly_scores - min_s) / (max_s - min_s + 1e-9) * 100, 0, 100)

    features_df["anomaly_score"] = anomaly_scores
    features_df["risk_score"] = risk_score
    features_df["risk_category"] = features_df["risk_score"].apply(
        lambda s: "Critical" if s >= 80 else "High" if s >= 60 else "Medium" if s >= 30 else "Low"
    )

    return features_df.sort_values("risk_score", ascending=False)