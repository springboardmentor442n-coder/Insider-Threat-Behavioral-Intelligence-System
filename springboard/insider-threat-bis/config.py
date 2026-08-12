"""Central configuration for the Insider Threat Behavioral Intelligence System."""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


class Config:
    # --- Paths -----------------------------------------------------------
    BASE_DIR = BASE_DIR
    DATA_DIR = BASE_DIR / "data"
    RAW_DIR = Path(os.getenv("CERT_RAW_DIR", DATA_DIR / "raw"))
    MODEL_DIR = BASE_DIR / "ml_model"
    FEATURES_CSV = DATA_DIR / "daily_user_features.csv"
    INSTANCE_DIR = BASE_DIR / "instance"

    # --- Flask -----------------------------------------------------------
    # Long enough to satisfy the HS256 key-length recommendation. It is a
    # published constant, so it is only safe for local development —
    # create_app() logs a warning when it is still in use.
    DEV_SECRET = "dev-only-insecure-secret-key-change-before-deploying"
    SECRET_KEY = os.getenv("SECRET_KEY", DEV_SECRET)
    JSON_SORT_KEYS = False

    # --- Auth ------------------------------------------------------------
    JWT_SECRET = os.getenv("JWT_SECRET", SECRET_KEY)
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRY_MINUTES = int(os.getenv("JWT_EXPIRY_MINUTES", "480"))

    # Seed analyst accounts created on first boot: username -> (password, role)
    SEED_ANALYSTS = {
        "admin": (os.getenv("ADMIN_PASSWORD", "admin123"), "admin"),
        "analyst": (os.getenv("ANALYST_PASSWORD", "analyst123"), "analyst"),
        "viewer": (os.getenv("VIEWER_PASSWORD", "viewer123"), "viewer"),
    }

    # --- Database --------------------------------------------------------
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", f"sqlite:///{INSTANCE_DIR / 'itbis.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- Risk engine -----------------------------------------------------
    # Weighted UEBA indicators, straight from the risk model spec.
    RISK_WEIGHTS = {
        "files_copied_to_usb": 3.0,
        "off_hours_usb": 3.0,
        "external_emails_sent": 3.0,
        "off_hours_logons": 2.0,
        "cloud_job_visits": 2.0,
    }
    # Blend of the weighted behavioural score and the ML probability.
    UEBA_WEIGHT = float(os.getenv("UEBA_WEIGHT", "0.55"))
    ML_WEIGHT = float(os.getenv("ML_WEIGHT", "0.45"))

    SEVERITY_THRESHOLDS = [(80, "CRITICAL"), (60, "HIGH"), (40, "MEDIUM"), (0, "LOW")]
    ALERT_THRESHOLD = float(os.getenv("ALERT_THRESHOLD", "60"))

    # --- Live monitoring -------------------------------------------------
    STREAM_INTERVAL_SECONDS = float(os.getenv("STREAM_INTERVAL_SECONDS", "1.5"))
    STREAM_BUFFER_SIZE = 500

    @classmethod
    def ensure_dirs(cls):
        for d in (cls.DATA_DIR, cls.RAW_DIR, cls.MODEL_DIR, cls.INSTANCE_DIR):
            d.mkdir(parents=True, exist_ok=True)
