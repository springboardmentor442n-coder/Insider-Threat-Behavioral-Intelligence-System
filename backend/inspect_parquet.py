from pathlib import Path
import duckdb

PROJECT_ROOT = Path(__file__).resolve().parent.parent

FILES = [
    PROJECT_ROOT / "datasets" / "integrated" / "employee_event_timeline.parquet",
    PROJECT_ROOT / "datasets" / "features" / "employee_risk_scores.parquet",
    PROJECT_ROOT / "datasets" / "predictions" / "all_model_predictions.parquet",
    PROJECT_ROOT / "datasets" / "exports" / "employee_final_risk_report.parquet",
]

for file in FILES:
    print("=" * 80)
    print(file)
    print("=" * 80)

    print("Exists:", file.exists())

    if not file.exists():
        continue

    df = duckdb.sql(
        f"SELECT * FROM read_parquet('{file.as_posix()}') LIMIT 5"
    ).df()

    print("\nColumns:\n")
    print(df.columns.tolist())

    print("\nSample:\n")
    print(df.head())
    