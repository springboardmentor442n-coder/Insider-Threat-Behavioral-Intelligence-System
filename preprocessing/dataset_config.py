"""
Dataset Configuration
AI Insider Threat Detection System
"""

import os

# Project Root
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# -----------------------------
# RAW DATASET
# -----------------------------

RAW_DATASET = os.path.join(PROJECT_ROOT, "dataset", "raw")

LOGON_FILE = os.path.join(RAW_DATASET, "logon.csv")
DEVICE_FILE = os.path.join(RAW_DATASET, "device.csv")
EMAIL_FILE = os.path.join(RAW_DATASET, "email.csv")
FILE_FILE = os.path.join(RAW_DATASET, "file.csv")
HTTP_FILE = os.path.join(RAW_DATASET, "http.csv")
PSYCHOMETRIC_FILE = os.path.join(RAW_DATASET, "psychometric.csv")

LDAP_FOLDER = os.path.join(RAW_DATASET, "LDAP")
ANSWERS_FOLDER = os.path.join(RAW_DATASET, "answers")


# -----------------------------
# PROCESSED DATASET
# -----------------------------

PROCESSED_DATASET = os.path.join(
    PROJECT_ROOT,
    "dataset",
    "processed"
)

os.makedirs(PROCESSED_DATASET, exist_ok=True)


LOGIN_FEATURES = os.path.join(
    PROCESSED_DATASET,
    "login_features.csv"
)

DEVICE_FEATURES = os.path.join(
    PROCESSED_DATASET,
    "device_features.csv"
)

EMAIL_FEATURES = os.path.join(
    PROCESSED_DATASET,
    "email_features.csv"
)

FILE_FEATURES = os.path.join(
    PROCESSED_DATASET,
    "file_features.csv"
)

HTTP_FEATURES = os.path.join(
    PROCESSED_DATASET,
    "http_features.csv"
)

PSYCHOMETRIC_FEATURES = os.path.join(
    PROCESSED_DATASET,
    "psychometric_features.csv"
)

LDAP_FEATURES = os.path.join(
    PROCESSED_DATASET,
    "ldap_features.csv"
)

EMPLOYEE_FEATURES = os.path.join(
    PROCESSED_DATASET,
    "employee_features.csv"
)