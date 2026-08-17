
import numpy as np
import pandas as pd
import joblib
import streamlit as st
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / ".." / "MODELS" / "random_forest_model.pkl"
DATA_PATH = BASE_DIR / ".." / "DATA" / "processed" / "labeled_dataset.csv"
CSS_PATH = BASE_DIR / "style.css"


@st.cache_data
def get_feature_names():
    df = pd.read_csv(DATA_PATH)
    return list(df.drop(columns=["user", "label"]).columns)


@st.cache_data
def get_float_features():
    df = pd.read_csv(DATA_PATH)
    features = [c for c in df.columns if c not in ("user", "label")]
    return frozenset(
        c for c in features if pd.api.types.is_float_dtype(df[c])
    )


@st.cache_resource
def load_model():
    model = joblib.load(MODEL_PATH)
    model.feature_names_in_ = np.asarray(get_feature_names())
    return model


def load_css():
    css = CSS_PATH.read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
