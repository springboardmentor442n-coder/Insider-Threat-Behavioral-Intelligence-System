import pandas as pd
import joblib

from pathlib import Path
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

PROCESSED_DATA = Path("dataset/processed")
MODEL_PATH = Path("ml/models/random_forest_model.pkl")

print("=" * 50)
print("INSIDER THREAT MODEL EVALUATION")
print("=" * 50)

print("\nLoading trained model...")
model = joblib.load(MODEL_PATH)
print("Model loaded successfully!")

print("\nLoading feature dataset...")
df = pd.read_csv(PROCESSED_DATA / "logon_features.csv")

df["target"] = df["late_night_login"]

features = [
    "login_count",
    "unique_pc_count",
    "is_weekend",
    "hour"
]

X = df[features]
y = df["target"]

print("\nMaking predictions...")
y_pred = model.predict(X)

accuracy = accuracy_score(y, y_pred)

print("\nAccuracy:")
print(accuracy)

print("\nClassification Report:")
print(classification_report(y, y_pred))

print("\nConfusion Matrix:")
print(confusion_matrix(y, y_pred))