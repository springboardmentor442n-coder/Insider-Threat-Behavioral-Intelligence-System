import joblib
import pandas as pd
from pathlib import Path
from sqlalchemy.orm import Session

from ml.preprocess import preprocess_logon
from ml.feature_engineering import generate_features

from backend.models import Prediction, Employee, BehaviorFeature
from backend.crud import (
    save_predictions_bulk,
    clear_predictions,
)


# -------------------------------------------------
# Paths
# -------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

PROCESSED_DATA = BASE_DIR / "dataset" / "processed"

MODEL_PATH = (
    BASE_DIR
    / "ml"
    / "models"
    / "random_forest_model.pkl"
)
LDAP_FILE = (
    BASE_DIR
    / "dataset"
    / "raw"
    / "LDAP"
)
# -------------------------------------------------
# Import Employees
# -------------------------------------------------
from pathlib import Path

def import_employees(ldap_folder, db: Session):

    print("=" * 60)
    print("IMPORT EMPLOYEES STARTED")
    print("=" * 60)

    ldap_files = sorted(Path(ldap_folder).glob("*.csv"))

    ldap_df = pd.concat(
        [pd.read_csv(f) for f in ldap_files],
        ignore_index=True
    )

    ldap_df = ldap_df.drop_duplicates(subset=["user_id"])

    # Clear old employee data
    db.query(Employee).delete()

    employee_objects = []

    for _, row in ldap_df.iterrows():

        employee_objects.append(

            Employee(

                employee_id=row["user_id"],

                name=row["employee_name"],

                department=row["department"],

                designation=row["role"],

                email=row["email"]

            )

        )

    db.bulk_save_objects(employee_objects)

    db.commit()

    print(f"Imported {len(employee_objects)} employees")
    print("=" * 60)
# -------------------------------------------------
# Main Pipeline
# -------------------------------------------------

def run_pipeline(input_csv, db: Session):

    print("=" * 60)
    print("RUNNING INSIDER THREAT PIPELINE")
    print("=" * 60)

    # -----------------------------------------
    # Step 1 : Preprocess
    # -----------------------------------------

    processed_file = (
        PROCESSED_DATA
        / "logon_processed.csv"
    )

    preprocess_logon(
        input_csv,
        processed_file
    )

    # -----------------------------------------
    # Step 2 : Feature Engineering
    # -----------------------------------------

    feature_file = (
        PROCESSED_DATA
        / "logon_features.csv"
    )

    generate_features(
        processed_file,
        feature_file
    )

    # -----------------------------------------
    # Step 3 : Load Feature Data
    # -----------------------------------------

    df = pd.read_csv(feature_file)

    print(f"Rows Loaded : {len(df)}")

    # -----------------------------------------
    # Step 4 : Import Employees
    # -----------------------------------------

    import_employees(LDAP_FILE, db)

    # -----------------------------------------
    # Step 5 : Load Model
    # -----------------------------------------

    model = joblib.load(MODEL_PATH)

    # -----------------------------------------
    # Step 6 : Prediction
    # -----------------------------------------

    X = df[
        [
            "login_count",
            "unique_pc_count"
        ]
    ].copy()

    # Keep the same feature names as the trained model
    X["is_weekend"] = (df["weekend_logins"] > 0).astype(int)
    X["hour"] = df["average_login_hour"].fillna(0).astype(int)

    predictions = model.predict(X)

    confidence = model.predict_proba(X).max(axis=1)

    df["prediction"] = predictions

    df["risk_level"] = df["prediction"].map(
        {
            1: "HIGH",
            0: "LOW"
        }
    )

    df["confidence"] = confidence * 100

    # -----------------------------------------
    # Step 7 : Save CSV
    # -----------------------------------------

    output_file = (
        PROCESSED_DATA
        / "prediction_results.csv"
    )

    df.to_csv(
        output_file,
        index=False
    )

    print("Prediction CSV Saved")

    # -----------------------------------------
    # Step 8 : Store Predictions
    # -----------------------------------------

    clear_predictions(db)

    prediction_objects = []

    for _, row in df.iterrows():

        prediction_objects.append(

            Prediction(

                employee_id=row["employee_id"],

                login_count=int(row["login_count"]),

                unique_pc_count=int(row["unique_pc_count"]),

                is_weekend=int(row["weekend_logins"] > 0),

                hour=int(row["average_login_hour"]),

                prediction=int(row["prediction"]),

                risk_level=row["risk_level"],

                confidence=float(row["confidence"])
            )

        )

    save_predictions_bulk(
        db,
        prediction_objects
    )

    print("=" * 60)
    print("PIPELINE COMPLETED")
    print("=" * 60)

    return {

        "status": "success",

        "employees_imported": int(
            df["employee_id"].nunique()
        ),

        "rows_processed": int(
            len(df)
        ),

        "high_risk": int(
            (df["prediction"] == 1).sum()
        ),

        "low_risk": int(
            (df["prediction"] == 0).sum()
        ),

        "predictions_saved": len(
            prediction_objects
        ),

        "output_file": str(
            output_file
        )
    }

  