from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl
from typing import List, Optional
import os


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Insider Threat Behavioral Intelligence System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]

    # Database (MySQL)
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = "password"
    DB_NAME: str = "insider_threat_db"
    DATABASE_URL: Optional[str] = None

    @property
    def db_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # JWT
    SECRET_KEY: str = "changethisinproduction-atleast32characters!!"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "noreply@insiderthreat.com"

    # ML
    MODEL_PATH: str = "./app/ml/models"
    CERT_DATASET_PATH: str = "./data/cert"

    # Risk Scoring Weights (must sum to 1.0)
    WEIGHT_BEHAVIORAL_ANOMALIES: float = 0.35
    WEIGHT_PRIVILEGE_MISUSE: float = 0.25
    WEIGHT_DATA_ACCESS_VIOLATIONS: float = 0.20
    WEIGHT_ACCESS_PATTERN_DEVIATIONS: float = 0.10
    WEIGHT_HISTORICAL_SECURITY_EVENTS: float = 0.10

    # Risk Thresholds
    RISK_THRESHOLD_LOW: int = 25
    RISK_THRESHOLD_MEDIUM: int = 50
    RISK_THRESHOLD_HIGH: int = 75
    RISK_THRESHOLD_CRITICAL: int = 90

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
