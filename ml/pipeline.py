import joblib
import pandas as pd
from pathlib import Path

from ml.preprocess import preprocess_logon
from ml.feature_engineering import generate_features

from backend.models import Prediction
from backend.crud import (
    save_predictions_bulk,
    clear_predictions,
)


BASE_DIR = Path(__file__).resolve().parent.parent

PROCESSED_DATA = BASE_DIR / "dataset" / "processed"
MODEL_PATH = BASE_DIR / "ml" / "models" / "random_forest_model.pkl"


def run_pipeline(input_csv, db):
    print("=" * 60)
    print("RUNNING INSIDER THREAT PIPELINE")
    print("=" * 60)

    # -----------------------------
    # Step 1 : Preprocess
    # -----------------------------
    processed_file = PROCESSED_DATA / "logon_processed.csv"

    preprocess_logon(
        input_csv,
        processed_file
    )

    # -----------------------------
    # Step 2 : Feature Engineering
    # -----------------------------
    feature_file = PROCESSED_DATA / "logon_features.csv"

    generate_features(
        processed_file,
        feature_file
    )

    # -----------------------------
    # Step 3 : Load Engineered Data
    # -----------------------------
    df = pd.read_csv(feature_file)

    # -----------------------------
    # Step 4 : Load Model
    # -----------------------------
    model = joblib.load(MODEL_PATH)

    # -----------------------------
    # Step 5 : Features
    # -----------------------------
    X = df[
        [
            "login_count",
            "unique_pc_count",
            "is_weekend",
            "hour"
        ]
    ]

    # -----------------------------
    # Step 6 : Predict
    # -----------------------------
    predictions = model.predict(X)
    confidence = model.predict_proba(X).max(axis=1)

    df["prediction"] = predictions
    df["risk_level"] = df["prediction"].map(
        {1: "HIGH", 0: "LOW"}
    )

    df["confidence"] = confidence * 100

    # -----------------------------
    # Step 7 : Save CSV
    # -----------------------------
    output_file = PROCESSED_DATA / "prediction_results.csv"

    df.to_csv(output_file, index=False)

    # -----------------------------
    # Step 8 : Store HIGH Risk Only
    # -----------------------------
    high_risk_rows = df[df["prediction"] == 1]

    prediction_objects = []

    for _, row in high_risk_rows.iterrows():

        prediction_objects.append(

            Prediction(

                employee_id=row["user"],

                login_count=int(row["login_count"]),

                unique_pc_count=int(row["unique_pc_count"]),

                is_weekend=int(row["is_weekend"]),

                hour=int(row["hour"]),

                prediction=int(row["prediction"]),

                risk_level=row["risk_level"],

                confidence=float(row["confidence"])

            )

        )
    # Remove previous pipeline results
    clear_predictions(db)
    
    save_predictions_bulk(
        db,
        prediction_objects
    )

    print("Pipeline Completed Successfully!")

    return {

        "rows_processed": len(df),

        "high_risk": len(high_risk_rows),

        "low_risk": len(df) - len(high_risk_rows),

        "saved_to_database": len(prediction_objects),

        "output_file": str(output_file)

    }