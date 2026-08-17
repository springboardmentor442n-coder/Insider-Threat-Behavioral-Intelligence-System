
import sys
import numpy as np
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import utils

MODEL = utils.load_model()
FEATURE_NAMES = utils.get_feature_names()

LOW_THRESHOLD = 0.30
HIGH_THRESHOLD = 0.45


def risk_level(prob):
    if prob < LOW_THRESHOLD:
        return "🟢 Low"
    if prob < HIGH_THRESHOLD:
        return "🟡 Medium"
    return "🔴 High"


def predict_single(features):
    input_df = pd.DataFrame([features], columns=FEATURE_NAMES)
    prediction = int(MODEL.predict(input_df)[0])
    probability = MODEL.predict_proba(input_df)[0]
    return prediction, probability


def predict_batch(data):
    df = data[FEATURE_NAMES].copy()
    predictions = MODEL.predict(df)
    probabilities = MODEL.predict_proba(df)
    df["Prediction"] = predictions
    df["Normal Probability"] = probabilities[:, 0]
    df["Insider Probability"] = probabilities[:, 1]
    df["Risk Level"] = [risk_level(p) for p in probabilities[:, 1]]
    return df
