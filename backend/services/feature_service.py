"""
feature_service.py

Behavioral Feature Extraction Service
-------------------------------------
This service scans the CERT Insider Threat dataset once,
extracts behavioral features for every employee,
and caches them in memory.

Author: ChatGPT
"""

from __future__ import annotations

from datetime import datetime

import pandas as pd

from backend.settings import settings


# ==========================================================
# Dataset Location
# ==========================================================

DATA_DIR = settings.backend_data_dir

LOGON_FILE = DATA_DIR / "logon.csv"
DEVICE_FILE = DATA_DIR / "device.csv"
EMAIL_FILE = DATA_DIR / "email.csv"
HTTP_FILE = DATA_DIR / "http.csv"
FILE_FILE = DATA_DIR / "file.csv"


# ==========================================================
# Cache
# ==========================================================

_employee_profiles = {}
_loaded = False


# ==========================================================
# Suspicious Website Categories
# ==========================================================

FILE_SHARING = {
    "dropbox",
    "drive.google",
    "mega",
    "wetransfer",
    "onedrive",
    "box.com",
}

SOCIAL_MEDIA = {
    "facebook",
    "twitter",
    "instagram",
    "reddit",
}

JOB_PORTALS = {
    "linkedin",
    "indeed",
    "glassdoor",
    "monster",
    "naukri",
}

DEVELOPER = {
    "github",
    "stackoverflow",
}


# ==========================================================
# Employee Profile Template
# ==========================================================

def create_employee():
    return {

        # -----------------------------
        # Login
        # -----------------------------
        "logons": 0,
        "logoffs": 0,
        "night_logins": 0,
        "weekend_logins": 0,
        "unique_pcs": set(),

        # -----------------------------
        # USB
        # -----------------------------
        "usb_connects": 0,
        "usb_disconnects": 0,

        # -----------------------------
        # Email
        # -----------------------------
        "emails_sent": 0,
        "attachments": 0,
        "large_attachments": 0,
        "external_emails": 0,

        # -----------------------------
        # HTTP
        # -----------------------------
        "http_requests": 0,

        "file_sharing": 0,
        "social_media": 0,
        "job_sites": 0,
        "developer_sites": 0,

        # -----------------------------
        # Files
        # -----------------------------
        "file_access": 0,

        "documents": 0,
        "pdfs": 0,
        "images": 0,
        "text_files": 0,
        "archives": 0,
        "executables": 0,
    }


# ==========================================================
# Utilities
# ==========================================================

def parse_date(value):

    try:
        return datetime.strptime(value, "%m/%d/%Y %H:%M:%S")
    except Exception:
        return None


def is_night_login(dt):

    return dt.hour >= 22 or dt.hour < 6


def is_weekend(dt):

    return dt.weekday() >= 5


def profile(user):

    if user not in _employee_profiles:
        _employee_profiles[user] = create_employee()

    return _employee_profiles[user]


# ==========================================================
# Logon Processing
# ==========================================================

def process_logon():

    print("Loading logon.csv ...")

    for chunk in pd.read_csv(LOGON_FILE, chunksize=100000):

        for _, row in chunk.iterrows():

            user = str(row["user"]).strip()

            emp = profile(user)

            dt = parse_date(str(row["date"]))

            activity = str(row["activity"]).strip()

            pc = str(row["pc"]).strip()

            emp["unique_pcs"].add(pc)

            if activity == "Logon":

                emp["logons"] += 1

                if dt:

                    if is_night_login(dt):
                        emp["night_logins"] += 1

                    if is_weekend(dt):
                        emp["weekend_logins"] += 1

            elif activity == "Logoff":

                emp["logoffs"] += 1

    print("Logon processing complete.")


# ==========================================================
# Device Processing
# ==========================================================

def process_device():

    print("Loading device.csv ...")

    for chunk in pd.read_csv(DEVICE_FILE, chunksize=100000):

        for _, row in chunk.iterrows():

            user = str(row["user"]).strip()

            emp = profile(user)

            activity = str(row["activity"]).strip()

            if activity == "Connect":

                emp["usb_connects"] += 1

            elif activity == "Disconnect":

                emp["usb_disconnects"] += 1

    print("Device processing complete.")
    # ==========================================================
# Email Processing
# ==========================================================

def process_email():

    print("Loading email.csv ...")

    for chunk in pd.read_csv(EMAIL_FILE, chunksize=100000):

        for _, row in chunk.iterrows():

            user = str(row["user"]).strip()

            emp = profile(user)

            emp["emails_sent"] += 1

            # ----------------------------
            # Attachments
            # ----------------------------

            try:
                attachments = int(row["attachments"])
            except:
                attachments = 0

            emp["attachments"] += attachments

            # ----------------------------
            # Large Emails (>1 MB)
            # ----------------------------

            try:
                size = int(row["size"])
            except:
                size = 0

            if size >= 1_000_000:
                emp["large_attachments"] += 1

            # ----------------------------
            # External Email Detection
            # ----------------------------

            recipients = []

            for col in ["to", "cc", "bcc"]:

                value = str(row[col])

                if value != "nan":

                    recipients.extend(value.split(";"))

            external = False

            for email in recipients:

                email = email.strip().lower()

                if email and not email.endswith("@dtaa.com"):

                    external = True
                    break

            if external:
                emp["external_emails"] += 1

    print("Email processing complete.")


# ==========================================================
# HTTP Processing
# ==========================================================

def process_http():

    print("Loading http.csv ...")

    count = 0

    for chunk in pd.read_csv(
        HTTP_FILE,
        usecols=["user", "url"],
        chunksize=100000
    ):

        for user, url in zip(chunk["user"], chunk["url"]):

            emp = profile(str(user).strip())

            emp["http_requests"] += 1

            url = str(url).lower()

            if any(site in url for site in FILE_SHARING):
                emp["file_sharing"] += 1

            elif any(site in url for site in SOCIAL_MEDIA):
                emp["social_media"] += 1

            elif any(site in url for site in JOB_PORTALS):
                emp["job_sites"] += 1

            elif any(site in url for site in DEVELOPER):
                emp["developer_sites"] += 1

        count += len(chunk)
        print(f"Processed {count} HTTP rows")

    print("HTTP processing complete.")


# ==========================================================
# File Processing
# ==========================================================

def process_file():

    print("Loading file.csv ...")

    for chunk in pd.read_csv(FILE_FILE, chunksize=100000):

        for _, row in chunk.iterrows():

            user = str(row["user"]).strip()

            emp = profile(user)

            emp["file_access"] += 1

            filename = str(row["filename"]).lower()

            if filename.endswith(".doc") or filename.endswith(".docx"):
                emp["documents"] += 1

            elif filename.endswith(".pdf"):
                emp["pdfs"] += 1

            elif filename.endswith(".txt"):
                emp["text_files"] += 1

            elif filename.endswith(".jpg") or \
                 filename.endswith(".jpeg") or \
                 filename.endswith(".png"):
                emp["images"] += 1

            elif filename.endswith(".zip") or \
                 filename.endswith(".rar") or \
                 filename.endswith(".7z"):
                emp["archives"] += 1

            elif filename.endswith(".exe") or \
                 filename.endswith(".bat") or \
                 filename.endswith(".msi"):
                emp["executables"] += 1

    print("File processing complete.")


# ==========================================================
# Finalization
# ==========================================================

def finalize_profiles():

    print("Finalizing employee profiles...")

    for employee in _employee_profiles.values():

        employee["unique_pcs"] = len(employee["unique_pcs"])

    print("Done.")


# ==========================================================
# Loader
# ==========================================================

def load_profiles():

    global _loaded

    if _loaded:
        return

    print("=" * 60)
    print("Loading Behavioral Feature Dataset")
    print("=" * 60)

    process_logon()
    process_device()
    process_email()
    process_http()
    process_file()

    finalize_profiles()

    _loaded = True

    print("=" * 60)
    print(f"Loaded {_employee_profiles.__len__()} employee profiles")
    print("=" * 60)


# ==========================================================
# Public APIs
# ==========================================================

def get_employee_profile(username: str):

    load_profiles()

    return _employee_profiles.get(username)


def get_all_profiles():

    load_profiles()

    return _employee_profiles


def employee_exists(username: str):

    load_profiles()

    return username in _employee_profiles


def reload_profiles():

    global _loaded

    _employee_profiles.clear()

    _loaded = False

    load_profiles()


# ==========================================================
# Test
# ==========================================================

if __name__ == "__main__":

    load_profiles()

    print()

    print(get_employee_profile("MOH0273"))
