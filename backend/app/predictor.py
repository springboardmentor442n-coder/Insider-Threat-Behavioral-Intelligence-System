import joblib
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODEL_PATH = PROJECT_ROOT / "ml" / "models" / "isolation_forest.pkl"

print("Loading model...")
model = joblib.load(MODEL_PATH)
print("Model loaded successfully!")


def predict(data):
    df = pd.DataFrame([data])

    prediction = model.predict(df)[0]

    if prediction == -1:
        return "INSIDER"
    else:
        return "NORMAL"