import os
import pandas as pd

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RESULTS_FILE = os.path.join(BASE_DIR, "final_behavioral_risk_results.csv")
OUTPUT_FILE = os.path.join(BASE_DIR, "employee_risk_summary.csv")


def build_employee_risk():

    df = pd.read_csv(RESULTS_FILE)

    # Convert numeric columns safely
    numeric_cols = [
        "prediction_probability",
        "ml_risk_score",
        "behavioral_risk_score",
        "final_risk_score"
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Employee-level aggregation
    employees = (
        df.groupby("user")
        .agg(
            prediction_probability=("prediction_probability", "mean"),
            ml_risk_score=("ml_risk_score", "mean"),
            behavioral_risk_score=("behavioral_risk_score", "mean"),
            final_risk_score=("final_risk_score", "mean"),
            prediction=("prediction", lambda x: x.mode().iloc[0]),
        )
        .reset_index()
    )

    # ---------------------------------------------------------
    # IMPORTANT:
    # Do NOT display raw 100 scores as the employee ranking.
    # Convert the employee ranking to a relative 30-90 display
    # scale while preserving the actual ordering.
    # ---------------------------------------------------------

    minimum = employees["final_risk_score"].min()
    maximum = employees["final_risk_score"].max()

    if maximum > minimum:
        employees["display_risk_score"] = (
            30
            + (
                (employees["final_risk_score"] - minimum)
                / (maximum - minimum)
            ) * 60
        )
    else:
        employees["display_risk_score"] = 60

    employees["display_risk_score"] = (
        employees["display_risk_score"]
        .round(1)
        .clip(30, 90)
    )

    # Never show exactly 100
    employees["display_risk_score"] = employees[
        "display_risk_score"
    ].clip(upper=90)

    # Employee severity based on displayed risk
    def severity(score):
        if score >= 75:
            return "Critical"
        elif score >= 60:
            return "High"
        elif score >= 45:
            return "Medium"
        return "Low"

    employees["severity"] = employees["display_risk_score"].apply(severity)

    employees = employees.sort_values(
        "display_risk_score",
        ascending=False
    )

    employees.to_csv(OUTPUT_FILE, index=False)

    print("Employee risk summary created.")
    print("Employees:", len(employees))
    print()
    print(
        employees[
            [
                "user",
                "display_risk_score",
                "prediction_probability",
                "ml_risk_score",
                "behavioral_risk_score",
                "severity"
            ]
        ].head(20).to_string(index=False)
    )


if __name__ == "__main__":
    build_employee_risk()