"""
Activity Service - Ingestion & Query Layer for CERT Activity Logs
"""

from backend.settings import settings
from backend.utils.data_loader import (
    load_csv,
    load_csv_preview,
)

DATA_PATH = settings.backend_data_dir

ACTIVITY_FILES = {
    "logon": DATA_PATH / "logon.csv",
    "device": DATA_PATH / "device.csv",
    "http": DATA_PATH / "http.csv",
    "email": DATA_PATH / "email.csv",
    "file": DATA_PATH / "file.csv",
}


# =============================================================================
# Activity Summary
# =============================================================================

def get_activity_summary():
    summary = {}
    for activity, path in ACTIVITY_FILES.items():
        df = load_csv_preview(path, rows=100)
        summary[activity] = {
            "available": not df.empty,
            "sample_count": len(df),
            "columns": list(df.columns) if not df.empty else [],
        }
    return summary


# =============================================================================
# Activity Types
# =============================================================================

def get_activity_types():
    return list(ACTIVITY_FILES.keys())


# =============================================================================
# Activity Statistics
# =============================================================================

def get_activity_statistics():
    stats = {}
    total_events = 0
    for activity, path in ACTIVITY_FILES.items():
        df = load_csv_preview(path, rows=1000)
        count = len(df)
        stats[activity] = count
        total_events += count

    return {
        "total_monitored_events": total_events,
        "activity_breakdown": stats,
        "monitored_categories": ["LOGIN", "FILE", "EMAIL", "HTTP", "USB", "PRIVILEGE", "REMOTE_ACCESS"],
    }


# =============================================================================
# Activity Timeline
# =============================================================================

def get_activity_timeline(limit=100):
    timeline = []
    for activity, path in ACTIVITY_FILES.items():
        df = load_csv_preview(path, rows=20)
        if not df.empty:
            for _, row in df.iterrows():
                item = row.to_dict()
                item["activity_category"] = activity.upper()
                timeline.append(item)

    return timeline[:limit]


# =============================================================================
# Activity Preview by Type
# =============================================================================

def get_activity(activity_type):
    activity_type = activity_type.lower()
    if activity_type not in ACTIVITY_FILES:
        return None

    df = load_csv_preview(
        ACTIVITY_FILES[activity_type],
        rows=100,
    )
    return df.to_dict(orient="records")


# =============================================================================
# Employee Activity
# =============================================================================

def get_employee_activity(employee_id):
    employee_logs = {}
    employee_id = employee_id.upper()

    for activity, path in ACTIVITY_FILES.items():
        df = load_csv(path)
        if df.empty or "user" not in df.columns:
            employee_logs[activity] = []
            continue

        filtered = df[df["user"].astype(str).str.upper() == employee_id]
        employee_logs[activity] = filtered.head(100).to_dict(orient="records")

    return employee_logs
