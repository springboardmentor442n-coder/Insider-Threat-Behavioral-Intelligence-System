"""
Risk Service

Reads ML-generated risk reports directly from CSV files.
"""

from backend.utils.config import (
    TOP_SUSPICIOUS,
    RISK_LEVEL_DISTRIBUTION,
)

from backend.utils.data_loader import load_csv


# ==========================================================
# Get All Risk Scores
# ==========================================================

def get_all_risk_scores():

    df = load_csv(TOP_SUSPICIOUS)

    if df.empty:
        return []

    df = df.sort_values(
        by="risk_score",
        ascending=False,
    )

    return df.to_dict(orient="records")


# ==========================================================
# Top High Risk Employees
# ==========================================================

def get_top_high_risk(limit=10):

    df = load_csv(TOP_SUSPICIOUS)

    if df.empty:
        return []

    df = df.sort_values(
        by="risk_score",
        ascending=False,
    )

    return df.head(limit).to_dict(orient="records")


# ==========================================================
# Employee Risk
# ==========================================================

def calculate_employee_risk(employee_id: str):

    df = load_csv(TOP_SUSPICIOUS)

    if df.empty:
        return None

    employee = df[
        df["user"].astype(str).str.upper()
        ==
        employee_id.upper()
    ]

    if employee.empty:
        return None

    return employee.iloc[0].to_dict()


# ==========================================================
# Risk Statistics
# ==========================================================

def get_risk_statistics():

    df = load_csv(RISK_LEVEL_DISTRIBUTION)

    if df.empty:
        return {}

    stats = {}

    for _, row in df.iterrows():

        stats[row["Risk Level"]] = {
            "employees": int(row["Employees"]),
            "percentage": float(row["Percentage"])
        }

    return stats
