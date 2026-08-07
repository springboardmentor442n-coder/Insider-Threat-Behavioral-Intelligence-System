import joblib
import pandas as pd
from pathlib import Path

# --------------------------------------------------
# Project Paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODEL_PATH = PROJECT_ROOT / "ml" / "models" / "isolation_forest.pkl"

# --------------------------------------------------
# Load Model
# --------------------------------------------------

print("Loading Isolation Forest model...")

model = joblib.load(MODEL_PATH)

print("Model loaded successfully!")

# --------------------------------------------------
# Prediction Function
# --------------------------------------------------

def predict_user(feature_row: pd.DataFrame) -> str:
    """
    Predict whether a user is NORMAL or INSIDER.

    Parameters
    ----------
    feature_row : pandas.DataFrame
        DataFrame containing exactly one employee's features.

    Returns
    -------
    str
        NORMAL or INSIDER
    """

    prediction = model.predict(feature_row)

    if prediction[0] == -1:
        return "INSIDER"

    return "NORMAL"