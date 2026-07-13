from fastapi import APIRouter, Header
from backend.schemas import PredictionRequest

import joblib
import pandas as pd
from pathlib import Path

from backend.security import verify_token
from fastapi import Depends
from sqlalchemy.orm import Session
from database.config import get_db
from database.crud import save_prediction, get_predictions

router = APIRouter()

MODEL_PATH = Path("ml/models/random_forest_model.pkl")
model = joblib.load(MODEL_PATH)

@router.post("/predict")
def predict(
    data: PredictionRequest, db: Session = Depends(get_db)):
    sample = pd.DataFrame([{
        "login_count": data.login_count,
        "unique_pc_count": data.unique_pc_count,
        "is_weekend": data.is_weekend,
        "hour": data.hour
    }])

    prediction = int(model.predict(sample)[0])
    probability = float(model.predict_proba(sample)[0][prediction])

    risk = "HIGH" if prediction == 1 else "LOW"
    save_prediction(
    db=db,
    login_count=data.login_count,
    unique_pc_count=data.unique_pc_count,
    is_weekend=data.is_weekend,
    hour=data.hour,
    prediction=prediction,
    risk_level=risk,
    confidence=round(probability * 100, 2)
)

    return {
        "prediction": prediction,
        "risk_level": risk,
        "confidence": round(probability * 100, 2)
    }

@router.get("/predictions")
def read_predictions(db: Session = Depends(get_db)):
    return get_predictions(db)