import time
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
    save_behavior_features,
)
from ml.http_features import HTTPFeatureExtractor
from ml.feature_builder import FeatureBuilder
from ml.email_features import EmailFeatureExtractor
from ml.file_features import FileFeatureExtractor
from ml.device_features import DeviceFeatureExtractor
from ml.explainable_ai import generate_risk_reasons

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
HTTP_FILE = (
    BASE_DIR
    / "dataset"
    / "raw"
    / "http.csv"
)
EMAIL_FILE = (
    BASE_DIR
    / "dataset"
    / "raw"
    / "email.csv"
)
FILE_FILE = (
    BASE_DIR
    / "dataset"
    / "raw"
    / "file.csv"
)
DEVICE_FILE = (
    BASE_DIR
    / "dataset"
    / "raw"
    / "device.csv"
)
FEATURE_COLUMNS_PATH = (
    BASE_DIR
    / "ml"
    / "models"
    / "feature_columns.pkl"
)

# -------------------------------------------------
# Import Employees
# -------------------------------------------------


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
def run_pipeline(
    dataset_folder,
    db: Session,
):

    print("=" * 60)
    print("RUNNING INSIDER THREAT PIPELINE")
    print("=" * 60)
    start_time = time.time()
    dataset_folder = Path(dataset_folder)

    LOGON_FILE = dataset_folder / "logon.csv"

    HTTP_FILE = dataset_folder / "http.csv"

    EMAIL_FILE = dataset_folder / "email.csv"

    FILE_FILE = dataset_folder / "file.csv"

    DEVICE_FILE = dataset_folder / "device.csv"

    LDAP_FOLDER = dataset_folder / "LDAP"
    required_files = {
        "logon.csv": LOGON_FILE,
        "http.csv": HTTP_FILE,
        "email.csv": EMAIL_FILE,
        "file.csv": FILE_FILE,
        "device.csv": DEVICE_FILE,
    }

    for dataset_name, dataset_path in required_files.items():

        if not Path(dataset_path).exists():

            raise FileNotFoundError(
                f"Required dataset '{dataset_name}' was not found.\n"
                f"Expected location: {dataset_path}"
            )

    if not Path(LDAP_FOLDER).exists():

        raise FileNotFoundError(
            f"LDAP folder not found:\n{LDAP_FOLDER}"
        )
    # -----------------------------------------
    # Step 1 : Preprocess
    # -----------------------------------------
    PROCESSED_DATA.mkdir(parents=True, exist_ok=True)
    processed_file = (
        PROCESSED_DATA
        / "logon_processed.csv"
    )

    preprocess_logon(
    LOGON_FILE,
    processed_file
)

    # -----------------------------------------
    # Step 2 : Feature Engineering
    # -----------------------------------------

    feature_file = (
        PROCESSED_DATA
        / "logon_features.csv"
    )

    df = generate_features(
        processed_file,
        feature_file
    )
        
    
    # -----------------------------------------
    # Step 3 : Load Feature Data
    # -----------------------------------------

    # -----------------------------------------
    # Step 3A : Initialize Feature Builder
    # -----------------------------------------

    builder = FeatureBuilder()

    builder.load_login_features(df)

    # -----------------------------------------
    # Step 3B : HTTP Feature Extraction
    # -----------------------------------------

    print("=" * 60)
    print("PROCESSING HTTP DATASET")
    print("=" * 60)

    http_extractor = HTTPFeatureExtractor()

    chunk_size = 500000

    for chunk in pd.read_csv(
        HTTP_FILE,
        chunksize=500000
    ):

        http_extractor.process_chunk(chunk)

    http_features = http_extractor.finalize()

    print(f"HTTP Users : {len(http_features)}")

    builder.merge_http_features(http_features)
    print("=" * 60)
    print("PROCESSING EMAIL DATASET")
    print("=" * 60)

    email_extractor = EmailFeatureExtractor()

    for chunk in pd.read_csv(
        EMAIL_FILE,
        chunksize=500000
    ):
        email_extractor.process_chunk(chunk)

    email_features = email_extractor.finalize()

    print(f"Email Users : {len(email_features)}")

    builder.merge_email_features(email_features)
    print("=" * 60)
    print("PROCESSING FILE DATASET")
    print("=" * 60)

    file_extractor = FileFeatureExtractor()

    for chunk in pd.read_csv(
        FILE_FILE,
        chunksize=500000
    ):
        file_extractor.process_chunk(chunk)

    file_features = file_extractor.finalize()

    print(f"File Users : {len(file_features)}")

    builder.merge_file_features(file_features)
    print("=" * 60)
    print("PROCESSING DEVICE DATASET")
    print("=" * 60)

    device_extractor = DeviceFeatureExtractor()

    for chunk in pd.read_csv(
        DEVICE_FILE,
        chunksize=500000
    ):
        device_extractor.process_chunk(chunk)

    device_features = device_extractor.finalize()

    print(f"Device Users : {len(device_features)}")

    builder.merge_device_features(device_features)

    # -----------------------------------------
    # Step 3C : Final Feature Table
    # -----------------------------------------

    df = builder.finalize()
    # -----------------------------------------
    # Save Combined Behavior Features
    # -----------------------------------------

    behavior_file = (
        PROCESSED_DATA
        / "behavior_features.csv"
    )

    df.to_csv(
        behavior_file,
        index=False
    )

    print("=" * 60)
    print("Behavior feature dataset saved")
    print(behavior_file)
    print("=" * 60)

    print("=" * 60)
    print(f"Rows Loaded : {len(df)}")

     # -----------------------------------------
    # Step 4: Import employees
    # -----------------------------------------
    import_employees(
        LDAP_FOLDER,
        db
    )

    print("=" * 60)
    print("SAVING BEHAVIOR FEATURES")
    print("=" * 60)

    save_behavior_features(db, df)

    # -----------------------------------------
    # Step 5 : Load Model
    # -----------------------------------------

    model = joblib.load(MODEL_PATH)
    feature_columns = joblib.load(
    FEATURE_COLUMNS_PATH
    )

    # -----------------------------------------
    # Step 6 : Prediction
    # -----------------------------------------
    X = df[feature_columns]

    predictions = model.predict(X)

    confidence = model.predict_proba(X).max(axis=1)
    df["risk_reasons"] = df.apply(
        lambda row: ", ".join(generate_risk_reasons(row)),
        axis=1
    )

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

                confidence=float(row["confidence"]),
                event_timestamp=row["event_timestamp"]
            )

        )

    save_predictions_bulk(
        db,
        prediction_objects
    )
    execution_time = round(
        time.time() - start_time,
        2
    )

    print()
    print("=" * 60)
    print("PIPELINE SUMMARY")
    print("=" * 60)

    print(f"Employees Imported      : {df['employee_id'].nunique()}")
    print(f"Behavior Profiles Saved : {len(df)}")
    print(f"Predictions Generated   : {len(prediction_objects)}")

    print()

    print(f"High Risk Employees     : {(df['prediction'] == 1).sum()}")
    print(f"Low Risk Employees      : {(df['prediction'] == 0).sum()}")

    print()

    print("Machine Learning Model  : Random Forest")
    print("Dataset                : CERT 4.2")
    print(f"Output CSV             : {output_file.name}")

    print()

    print(f"Execution Time         : {execution_time} seconds")

    print("=" * 60)
    print("PIPELINE COMPLETED SUCCESSFULLY")
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

  