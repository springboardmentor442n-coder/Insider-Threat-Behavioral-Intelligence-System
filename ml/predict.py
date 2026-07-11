import pandas as pd
import joblib
from pathlib import Path

PROCESSED_DATA = Path("dataset/processed")
MODEL_PATH = Path("ml/models/random_forest_model.pkl")

print("=" * 50)
print("INSIDER THREAT PREDICTION")
print("=" * 50)

print("\nLoading trained model...")
model = joblib.load(MODEL_PATH)
print("Model loaded successfully!")

print("\nLoading feature dataset...")
df = pd.read_csv(PROCESSED_DATA / "logon_features.csv")

features = [
    "login_count",
    "unique_pc_count",
    "is_weekend",
    "hour"
]

X = df[features]

print("\nMaking predictions...")
predictions = model.predict(X)

df["prediction"] = predictions

print(df[["user", "hour", "prediction"]].head(20))

prediction_file = PROCESSED_DATA / "prediction_results.csv"

df.to_csv(prediction_file, index=False)

print("\nPrediction results saved successfully!")
print(prediction_file)