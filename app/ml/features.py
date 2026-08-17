"""CERT r4.2 ingestion and daily user-level feature engineering.

This is a direct port of the notebook pipeline: raw activity logs
(logon / device / file / email / http) are aggregated into one row per
(user, day), then enriched with monthly LDAP organisational context.
"""

from __future__ import annotations

import glob
import os
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder

# Behavioural features produced by the aggregation stage.
BEHAVIOURAL_COLUMNS = [
    "logon_count",
    "off_hours_logons",
    "distinct_pcs",
    "usb_connects",
    "off_hours_usb",
    "files_copied_to_usb",
    "sensitive_files_to_usb",
    "total_emails_sent",
    "external_emails_sent",
    "total_attachments",
    "total_email_size",
    "http_requests",
    "cloud_job_visits",
]

# LDAP context columns kept for modelling. `team_encoded` is dropped: it is
# almost collinear with department and had the worst LDAP coverage.
LDAP_COLUMNS = ["role_encoded", "department_encoded", "supervisor_encoded"]

FEATURE_COLUMNS = BEHAVIOURAL_COLUMNS + LDAP_COLUMNS

# Human-readable labels for the console.
FEATURE_LABELS = {
    "logon_count": "Logons",
    "off_hours_logons": "Off-Hours Logons",
    "distinct_pcs": "Distinct PCs Used",
    "usb_connects": "USB Connections",
    "off_hours_usb": "Off-Hours USB Activity",
    "files_copied_to_usb": "Files Copied to USB",
    "sensitive_files_to_usb": "Sensitive Files to USB",
    "total_emails_sent": "Emails Sent",
    "external_emails_sent": "External Emails Sent",
    "total_attachments": "Email Attachments",
    "total_email_size": "Total Email Size (bytes)",
    "http_requests": "HTTP Requests",
    "cloud_job_visits": "Cloud / Job-Site Visits",
    "role_encoded": "Role (encoded)",
    "department_encoded": "Department (encoded)",
    "supervisor_encoded": "Supervisor (encoded)",
}

OFF_HOURS_START = 18  # 18:00 and later is off-hours
OFF_HOURS_END = 7  # before 07:00 is off-hours
INTERNAL_DOMAIN = "dtaa.com"


# ---------------------------------------------------------------------------
# Per-source aggregation
# ---------------------------------------------------------------------------
def _logon_features(logon: pd.DataFrame) -> pd.DataFrame:
    logon["day"] = logon["date"].dt.date
    logon["hour"] = logon["date"].dt.hour
    logon["is_off_hours"] = (
        (logon["hour"] < OFF_HOURS_END) | (logon["hour"] >= OFF_HOURS_START)
    ).astype(int)
    return (
        logon.groupby(["user", "day"])
        .agg(
            logon_count=("activity", lambda x: (x == "Logon").sum()),
            off_hours_logons=("is_off_hours", "sum"),
            distinct_pcs=("pc", "nunique"),
        )
        .reset_index()
    )


def _device_features(device: pd.DataFrame) -> pd.DataFrame:
    device["day"] = device["date"].dt.date
    device["hour"] = device["date"].dt.hour
    connects = device[device["activity"] == "Connect"].copy()
    connects["is_off_hours"] = (
        (connects["hour"] < OFF_HOURS_END) | (connects["hour"] >= OFF_HOURS_START)
    ).astype(int)
    return (
        connects.groupby(["user", "day"])
        .agg(
            usb_connects=("activity", "count"),
            off_hours_usb=("is_off_hours", "sum"),
        )
        .reset_index()
    )


def _file_features(file_df: pd.DataFrame) -> pd.DataFrame:
    file_df["day"] = file_df["date"].dt.date
    file_df["is_sensitive"] = (
        file_df["filename"]
        .str.contains(r"\.doc|\.pdf|\.zip", case=False, na=False)
        .astype(int)
    )
    return (
        file_df.groupby(["user", "day"])
        .agg(
            files_copied_to_usb=("filename", "count"),
            sensitive_files_to_usb=("is_sensitive", "sum"),
        )
        .reset_index()
    )


def _email_features(email: pd.DataFrame) -> pd.DataFrame:
    email["day"] = email["date"].dt.date
    email["is_external"] = (
        ~email["to"].str.contains(INTERNAL_DOMAIN, case=False, na=False)
    ).astype(int)

    if "attachment_count" in email.columns:
        source_col = "attachment_count"
    elif "attachments" in email.columns:
        source_col = "attachments"
    else:
        source_col = None

    if source_col is None:
        email["attachment_count"] = 0
    else:
        email["attachment_count"] = pd.to_numeric(
            email[source_col], errors="coerce"
        ).fillna(0)

    if "size" not in email.columns:
        email["size"] = 0
    email["size"] = pd.to_numeric(email["size"], errors="coerce").fillna(0)

    return (
        email.groupby(["user", "day"])
        .agg(
            total_emails_sent=("date", "count"),
            external_emails_sent=("is_external", "sum"),
            total_attachments=("attachment_count", "sum"),
            total_email_size=("size", "sum"),
        )
        .reset_index()
    )


def _http_features_chunked(path: str | Path, chunksize: int = 2_000_000) -> pd.DataFrame:
    """http.csv is the largest source (~28M rows on real r4.2) — stream it."""
    parts = []
    for chunk in pd.read_csv(path, parse_dates=["date"], chunksize=chunksize):
        chunk["day"] = chunk["date"].dt.date
        chunk["is_cloud_or_job"] = (
            chunk["url"]
            .str.contains("dropbox|drive|monster|linkedin", case=False, na=False)
            .astype(int)
        )
        parts.append(
            chunk.groupby(["user", "day"])
            .agg(
                http_requests=("date", "count"),
                cloud_job_visits=("is_cloud_or_job", "sum"),
            )
            .reset_index()
        )
    if not parts:
        return pd.DataFrame(columns=["user", "day", "http_requests", "cloud_job_visits"])
    # A user/day pair can straddle a chunk boundary, so re-sum after concat.
    return pd.concat(parts, ignore_index=True).groupby(["user", "day"]).sum().reset_index()


# ---------------------------------------------------------------------------
# LDAP organisational context
# ---------------------------------------------------------------------------
def _merge_ldap(combined: pd.DataFrame, raw_dir: Path) -> tuple[pd.DataFrame, dict]:
    ldap_files = sorted(glob.glob(str(raw_dir / "LDAP" / "*.csv")))
    combined["day"] = pd.to_datetime(combined["day"])

    if not ldap_files:
        for col in LDAP_COLUMNS:
            combined[col] = 0
        return combined, {}

    frames = []
    for path in ldap_files:
        df = pd.read_csv(path)
        df["month_year"] = os.path.basename(path).split(".csv")[0]
        frames.append(df)

    master = pd.concat(frames, ignore_index=True)
    master = master[["user_id", "month_year", "role", "department", "team", "supervisor"]]
    master = master.rename(columns={"user_id": "user"})

    # Guard against a monthly file carrying two rows for the same user: a plain
    # merge would silently fan out every activity row for that user that month.
    master = master.drop_duplicates(subset=["user", "month_year"], keep="last")

    combined["month_year"] = combined["day"].dt.strftime("%Y-%m")
    rows_before = len(combined)
    combined = combined.merge(master, on=["user", "month_year"], how="left")
    if len(combined) != rows_before:
        raise RuntimeError(
            f"LDAP merge duplicated rows: {rows_before} -> {len(combined)}"
        )

    combined = combined.sort_values(by=["user", "day"])
    cat_columns = ["role", "department", "team", "supervisor"]
    # Carry the last known org record forward for months with no LDAP snapshot.
    combined[cat_columns] = combined.groupby("user")[cat_columns].ffill()

    encoders = {}
    for col in cat_columns:
        combined[col] = combined[col].fillna("Unknown").astype(str)
        le = LabelEncoder()
        combined[f"{col}_encoded"] = le.fit_transform(combined[col])
        encoders[col] = le

    combined = combined.drop(columns=cat_columns + ["month_year", "team_encoded"])
    return combined, encoders


# ---------------------------------------------------------------------------
# Ground-truth labelling
# ---------------------------------------------------------------------------
ANSWER_SCHEMAS = {
    "logon": ["type", "id", "date", "user", "pc", "activity"],
    "device": ["type", "id", "date", "user", "pc", "activity"],
    "http": ["type", "id", "date", "user", "pc", "url", "content"],
    "file": ["type", "id", "date", "user", "pc", "filename", "content"],
    "email": [
        "type", "id", "date", "user", "pc", "to", "cc", "bcc",
        "from", "size", "attachment_count", "content",
    ],
}


def _parse_answer_file(path: str) -> list[list[str]]:
    """Answer files mix record types and contain unquoted commas in content."""
    rows = []
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.rstrip("\r\n")
            if not line:
                continue
            row_type = line.split(",", 1)[0]
            schema = ANSWER_SCHEMAS.get(row_type)
            if not schema:
                continue
            parts = line.split(",", len(schema) - 1)
            if len(parts) == len(schema):
                # (user, date) is all we need to mark a malicious user-day.
                rows.append([parts[schema.index("user")], parts[schema.index("date")]])
    return rows


def load_ground_truth(raw_dir: Path) -> pd.DataFrame | None:
    """Build the malicious (user, day) table from the CERT answers folder."""
    answers_dir = raw_dir / "answers"
    if not answers_dir.exists():
        return None

    rows = []
    for path in glob.glob(str(answers_dir / "**" / "*.csv"), recursive=True):
        if os.path.basename(path) == "insiders.csv":
            continue
        rows.extend(_parse_answer_file(path))

    if not rows:
        return None

    df = pd.DataFrame(rows, columns=["user", "date"])
    df["day"] = pd.to_datetime(df["date"], errors="coerce").dt.normalize()
    df = df.dropna(subset=["day"])[["user", "day"]].drop_duplicates()
    df["is_insider"] = 1
    return df


def heuristic_labels(combined: pd.DataFrame) -> pd.Series:
    """Fallback labelling when the CERT answer key is unavailable.

    Flags a user-day when exfiltration-shaped indicators run far above the
    population mean. Weaker than the real answer key, but it keeps the whole
    pipeline runnable end-to-end.
    """
    means = combined[BEHAVIOURAL_COLUMNS].mean()
    suspicious = (
        (combined["files_copied_to_usb"] > max(means["files_copied_to_usb"] * 4, 8))
        | (combined["off_hours_usb"] > max(means["off_hours_usb"] * 6, 2))
        | (combined["external_emails_sent"] > max(means["external_emails_sent"] * 4, 12))
        | (combined["cloud_job_visits"] > max(means["cloud_job_visits"] * 5, 12))
    )
    strong = suspicious & (
        combined["off_hours_logons"] > means["off_hours_logons"]
    )
    return strong.astype(int)


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------
def build_daily_features(raw_dir: str | Path, verbose: bool = True) -> pd.DataFrame:
    """Run the full ingestion pipeline over a CERT r4.2 style raw directory."""
    raw_dir = Path(raw_dir)

    def log(msg):
        if verbose:
            print(f"  {msg}")

    required = ["logon.csv", "device.csv", "file.csv", "email.csv", "http.csv"]
    missing = [f for f in required if not (raw_dir / f).exists()]
    if missing:
        raise FileNotFoundError(
            f"Missing raw log files in {raw_dir}: {', '.join(missing)}. "
            "Run `python scripts/generate_data.py` or point CERT_RAW_DIR at r4.2."
        )

    log("Reading logon.csv ...")
    logon = pd.read_csv(raw_dir / "logon.csv", parse_dates=["date"])
    log("Reading device.csv ...")
    device = pd.read_csv(raw_dir / "device.csv", parse_dates=["date"])
    log("Reading file.csv ...")
    file_df = pd.read_csv(raw_dir / "file.csv", parse_dates=["date"])
    log("Reading email.csv ...")
    email = pd.read_csv(raw_dir / "email.csv", parse_dates=["date"])

    log("Aggregating logon features ...")
    combined = _logon_features(logon)
    for name, fn, df in [
        ("device", _device_features, device),
        ("file", _file_features, file_df),
        ("email", _email_features, email),
    ]:
        log(f"Aggregating {name} features ...")
        combined = combined.merge(fn(df), on=["user", "day"], how="outer")

    log("Aggregating http features (chunked) ...")
    combined = combined.merge(
        _http_features_chunked(raw_dir / "http.csv"), on=["user", "day"], how="outer"
    )

    numeric_cols = combined.columns.difference(["user", "day"])
    combined[numeric_cols] = combined[numeric_cols].fillna(0)

    log("Merging LDAP organisational context ...")
    combined, _ = _merge_ldap(combined, raw_dir)

    log("Applying ground-truth labels ...")
    truth = load_ground_truth(raw_dir)
    combined["day"] = pd.to_datetime(combined["day"])
    if truth is not None:
        combined = combined.merge(truth, on=["user", "day"], how="left")
        combined["is_insider"] = combined["is_insider"].fillna(0).astype(int)
        log(f"Answer key matched {int(combined['is_insider'].sum())} malicious user-days")
    else:
        combined["is_insider"] = heuristic_labels(combined)
        log(
            "No answers/ folder found — used heuristic labels "
            f"({int(combined['is_insider'].sum())} flagged user-days)"
        )

    for col in FEATURE_COLUMNS:
        if col not in combined.columns:
            combined[col] = 0
        combined[col] = pd.to_numeric(combined[col], errors="coerce").fillna(0)

    combined = combined.sort_values(["day", "user"]).reset_index(drop=True)
    return combined[["user", "day"] + FEATURE_COLUMNS + ["is_insider"]]


def load_features(csv_path: str | Path) -> pd.DataFrame:
    """Load the engineered feature table produced by build_daily_features."""
    df = pd.read_csv(csv_path, parse_dates=["day"])
    for col in FEATURE_COLUMNS:
        if col not in df.columns:
            df[col] = 0
    df[FEATURE_COLUMNS] = df[FEATURE_COLUMNS].apply(
        pd.to_numeric, errors="coerce"
    ).fillna(0)
    if "is_insider" not in df.columns:
        df["is_insider"] = 0
    df["is_insider"] = df["is_insider"].fillna(0).astype(int)
    return df
