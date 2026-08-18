import pandas as pd
import joblib
from pathlib import Path
from sklearn.ensemble import IsolationForest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = PROJECT_ROOT / "datasets" / "processed" / "final_features.csv"
MODEL_PATH = PROJECT_ROOT / "ml" / "models"
OUTPUT_PATH = PROJECT_ROOT / "datasets" / "processed"

print("Loading final features...")
df = pd.read_csv(DATA_PATH)
print("Dataset Shape:", df.shape)

users = df["user"]
X = df.drop(columns=["user"])

# Enforce exact training feature order requested by user
expected_cols = [
    "device_connections",
    "emails_sent",
    "files_accessed",
    "websites_visited",
    "logon_count",
    "O",
    "C",
    "E",
    "A",
    "N"
]
X = X[expected_cols]

print("Feature Matrix Shape:", X.shape)
print("Features:", X.columns.tolist())

model = IsolationForest(
    n_estimators=100,
    contamination=0.05,
    random_state=42
)

print("Training model...")
model.fit(X)
print("Model trained successfully!")

predictions = model.predict(X)
df["prediction"] = predictions

print("Prediction Counts:")
print(df["prediction"].value_counts())

MODEL_PATH.mkdir(parents=True, exist_ok=True)
joblib.dump(model, MODEL_PATH / "isolation_forest.pkl")
print("Model saved to:", MODEL_PATH / "isolation_forest.pkl")

df.to_csv(OUTPUT_PATH / "prediction_results.csv", index=False)
print("Prediction results saved to:", OUTPUT_PATH / "prediction_results.csv")
