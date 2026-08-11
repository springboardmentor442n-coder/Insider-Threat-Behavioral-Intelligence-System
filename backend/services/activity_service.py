"""
Activity Service
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

        print(f"Checking {activity}...")

        df = load_csv_preview(path, rows=1)

        summary[activity] = {
            "available": not df.empty,
            "preview_rows": len(df),
        }

    return summary


# =============================================================================
# Activity Types
# =============================================================================

def get_activity_types():

    return list(ACTIVITY_FILES.keys())


# =============================================================================
# Activity Preview
# =============================================================================

def get_activity(activity_type):

    activity_type = activity_type.lower()

    if activity_type not in ACTIVITY_FILES:
        return None

    print(f"Loading preview for {activity_type}...")

    df = load_csv_preview(
        ACTIVITY_FILES[activity_type],
        rows=100,
    )

    print(f"Returned {len(df)} rows")

    return df.to_dict(orient="records")


# =============================================================================
# Employee Activity
# =============================================================================

def get_employee_activity(employee_id):

    employee_logs = {}

    employee_id = employee_id.upper()

    for activity, path in ACTIVITY_FILES.items():

        print(f"Searching {activity}...")

        df = load_csv(path)

        if df.empty:
            employee_logs[activity] = []
            continue

        if "user" not in df.columns:
            employee_logs[activity] = []
            continue

        filtered = df[
            df["user"].astype(str).str.upper()
            == employee_id
        ]

        employee_logs[activity] = (
            filtered
            .head(100)
            .to_dict(orient="records")
        )

    return employee_logs
