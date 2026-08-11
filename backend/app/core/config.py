import os
from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "Insider Threat Behavioral Intelligence System"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "insider-threat-secret-key-2026-super-secure-jwt-token"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 # 24 hours
    ALGORITHM: str = "HS256"
    
    # Paths
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    ML_MODELS_DIR: str = os.path.join(BASE_DIR, "ml", "models")
    DATASETS_DIR: str = os.path.join(BASE_DIR, "datasets")
    
    # Model Artifact Paths
    GB_MODEL_PATH: str = os.path.join(ML_MODELS_DIR, "gb.pkl")
    SCALER_PATH: str = os.path.join(ML_MODELS_DIR, "scaler.pkl")
    FEATURE_COLUMNS_PATH: str = os.path.join(ML_MODELS_DIR, "feature_columns.pkl")
    
    # Dataset Paths
    DAILY_FEATURES_CSV: str = os.path.join(DATASETS_DIR, "daily_behavioral_features.csv")
    RISK_RESULTS_CSV: str = os.path.join(DATASETS_DIR, "final_behavioral_risk_results.csv")
    
    # Database
    DATABASE_URL: str = f"sqlite:///{os.path.join(BASE_DIR, 'backend', 'insider_threat.db')}"

settings = Settings()
