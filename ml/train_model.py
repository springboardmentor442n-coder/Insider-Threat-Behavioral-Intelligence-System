import joblib
import pandas as pd
from pathlib import Path

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)
from sklearn.model_selection import train_test_split


# =====================================================
# Paths
# =====================================================

BASE_DIR = Path(__file__).resolve().parent.parent

PROCESSED_DATA = BASE_DIR / "dataset" / "processed"

MODEL_DIR = BASE_DIR / "ml" / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATH = MODEL_DIR / "random_forest_model.pkl"


# =====================================================
# Load Dataset
# =====================================================

print("=" * 60)
print("INSIDER THREAT MODEL TRAINING")
print("=" * 60)

print("\nLoading feature engineered dataset...")

df = pd.read_csv(
    PROCESSED_DATA / "behavior_features.csv"
)

print("Dataset loaded successfully!")

print("\nDataset Shape:")
print(df.shape)

print("\nColumns:")
print(df.columns.tolist())


# =====================================================
# Missing Values
# =====================================================

print("\nChecking missing values...")

df.fillna(0, inplace=True)

print("Missing values handled.")


# =====================================================
# Dynamic Risk Thresholds
# =====================================================

print("\nCalculating dynamic thresholds...")

http_threshold = df["http_visit_count"].quantile(0.95)
email_threshold = df["external_emails"].quantile(0.95)
device_threshold = df["device_usage_count"].quantile(0.95)
file_threshold = df["file_access_count"].quantile(0.95)

print(f"HTTP Threshold           : {http_threshold}")
print(f"External Email Threshold : {email_threshold}")
print(f"Device Threshold         : {device_threshold}")
print(f"File Threshold           : {file_threshold}")


# =====================================================
# Target Column
# =====================================================

print("\nCreating target labels...")

risk_score = (

    (df["after_hours_logins"] >= 5).astype(int)

    + (df["weekend_logins"] >= 3).astype(int)

    + (df["http_visit_count"] >= http_threshold).astype(int)

    + (df["external_emails"] >= email_threshold).astype(int)

    + (df["device_usage_count"] >= device_threshold).astype(int)

    + (df["file_access_count"] >= file_threshold).astype(int)

)

df["target"] = (risk_score >= 2).astype(int)

print("\nTarget Distribution")
print(df["target"].value_counts())


# =====================================================
# Features
# =====================================================

FEATURE_COLUMNS = [

    # Login
    "login_count",
    "unique_pc_count",
    "weekend_logins",
    "after_hours_logins",

    # HTTP
    "http_visit_count",
    "unique_websites",
    "after_hours_http",
    "weekend_http",
    "unique_http_pcs",

    # Email
    "email_sent",
    "external_emails",
    "after_hours_emails",

    # File
    "file_access_count",
    "unique_files",
    "after_hours_file_access",
    "weekend_file_access",

    # Device
    "device_usage_count",
    "connect_count",
    "disconnect_count",
    "after_hours_device_usage",
    "weekend_device_usage",

]

X = df[FEATURE_COLUMNS]

y = df["target"]


# =====================================================
# Train Test Split
# =====================================================

print("\nSplitting dataset...")

X_train, X_test, y_train, y_test = train_test_split(

    X,
    y,

    test_size=0.20,

    random_state=42,

    stratify=y

)

print(f"Training Samples : {len(X_train)}")
print(f"Testing Samples  : {len(X_test)}")


# =====================================================
# Train Model
# =====================================================

print("\nTraining Random Forest...")

model = RandomForestClassifier(

    n_estimators=100,

    random_state=42,

    n_jobs=-1

)

model.fit(X_train, y_train)

print("Model trained successfully!")


# =====================================================
# Prediction
# =====================================================

print("\nMaking predictions...")

y_pred = model.predict(X_test)


# =====================================================
# Evaluation
# =====================================================

accuracy = accuracy_score(y_test, y_pred)

print("\nAccuracy")
print(accuracy)

print("\nClassification Report")
print(classification_report(y_test, y_pred))

print("\nConfusion Matrix")
cm = confusion_matrix(y_test, y_pred)
print(cm)


# =====================================================
# Save Model
# =====================================================

joblib.dump(model, MODEL_PATH)

print("\nModel saved successfully!")

print(MODEL_PATH)


# =====================================================
# Save Feature List
# =====================================================

joblib.dump(
    FEATURE_COLUMNS,
    MODEL_DIR / "feature_columns.pkl"
)

print("Feature list saved.")


# =====================================================
# Feature Importance
# =====================================================

importance = pd.DataFrame({

    "Feature": FEATURE_COLUMNS,

    "Importance": model.feature_importances_

})

importance = importance.sort_values(

    by="Importance",

    ascending=False

)

print("\nFeature Importance")

print(importance)

importance.to_csv(

    PROCESSED_DATA / "feature_importance.csv",

    index=False

)


# =====================================================
# Save Metrics
# =====================================================

metrics = pd.DataFrame({

    "Metric": ["Accuracy"],

    "Value": [accuracy]

})

metrics.to_csv(

    PROCESSED_DATA / "training_metrics.csv",

    index=False

)

pd.DataFrame(

    cm,

    columns=["Predicted Low", "Predicted High"],

    index=["Actual Low", "Actual High"]

).to_csv(

    PROCESSED_DATA / "confusion_matrix.csv"

)

print("\nTraining completed successfully!")

print("=" * 60)