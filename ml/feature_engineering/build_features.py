from pathlib import Path
import polars as pl

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_PATH = PROJECT_ROOT / "datasets" / "processed"

# Load cleaned datasets
device = pl.read_csv(PROCESSED_PATH / "device_cleaned.csv")
email = pl.read_csv(PROCESSED_PATH / "email_cleaned.csv")
file = pl.read_csv(PROCESSED_PATH / "file_cleaned.csv")
http = pl.read_csv(PROCESSED_PATH / "http_cleaned.csv")
logon = pl.read_csv(PROCESSED_PATH / "logon_cleaned.csv")
psychometric = pl.read_csv(PROCESSED_PATH / "psychometric_cleaned.csv")


# Feature 1 : Login Count

login_count = (
    logon.group_by("user")
    .len()
    .rename({"len": "login_count"})
)

print(login_count.head())


# Feature 2 : HTTP Requests

http_count = (
    http.group_by("user")
    .len()
    .rename({"len": "http_requests"})
)

print(http_count.head())


# Feature 3 : Emails Sent

email_count = (
    email.group_by("user")
    .len()
    .rename({"len": "emails_sent"})
)

print("\nEmail Feature")
print(email_count.head())


# Feature 4 : Files Accessed

file_count = (
    file.group_by("user")
    .len()
    .rename({"len": "files_accessed"})
)

print("\nFile Feature")
print(file_count.head())


# Feature 5 : Device Activity

device_count = (
    device.group_by("user")
    .len()
    .rename({"len": "device_activity"})
)

print("\nDevice Feature")
print(device_count.head())


# Feature 6 : Psychometric

psychometric_features = psychometric.select([
    "user_id",
    "O",
    "C",
    "E",
    "A",
    "N"
])

print("\nPsychometric Feature")
print(psychometric_features.head())
