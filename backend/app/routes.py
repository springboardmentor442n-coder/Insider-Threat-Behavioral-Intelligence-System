from fastapi import APIRouter

from .schemas import UserFeatures
from .predictor import predict

router = APIRouter()


@router.get("/")
def home():
    return {
        "message": "Insider Threat Behavioral Intelligence System API is Running"
    }


@router.post("/predict")
def predict_user(user: UserFeatures):

    result = predict(user.model_dump())

    return {
        "prediction": result
    }