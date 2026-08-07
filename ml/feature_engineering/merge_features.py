"""
merge_features.py

Combines all engineered behavioral features into a single
machine learning dataset.
"""

from pathlib import Path
import polars as pl
PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROCESSED_PATH = PROJECT_ROOT / "datasets" / "processed"
device = pl.read_csv(PROCESSED_PATH / "device_cleaned.csv")
email = pl.read_csv(PROCESSED_PATH / "email_cleaned.csv")
file = pl.read_csv(PROCESSED_PATH / "file_cleaned.csv")
http = pl.read_csv(PROCESSED_PATH / "http_cleaned.csv")
logon = pl.read_csv(PROCESSED_PATH / "logon_cleaned.csv")
psychometric = pl.read_csv(PROCESSED_PATH / "psychometric_cleaned.csv")

device_feature = (
    device
    .group_by("user")
    .len()
    .rename({"len": "device_connections"})
)
email_feature = (
    email
    .group_by("user")
    .len()
    .rename({"len":"emails_sent"})
)
file_feature = (
    file
    .group_by("user")
    .len()
    .rename({"len": "files_accessed"})
)
http_feature = (
    http
    .group_by("user")
    .len()
    .rename({"len": "websites_visited"})
)
logon_feature = (
    logon
    .group_by("user")
    .len()
    .rename({"len": "logon_count"})
)

psychometric_feature = (
    psychometric
    .rename({"user_id": "user"})
    .select(
        [
            "user",
            "O",
            "C",
            "E",
            "A",
            "N"
        ]
    )
)

# ---------------------------------
# Merge Feature Tables
# ---------------------------------

features = device_feature.join(
    email_feature,
    on="user",
    how="left"
)
# Merge File Feature
features = features.join(
    file_feature,
    on="user",
    how="left"
)

# Merge HTTP Feature
features = features.join(
    http_feature,
    on="user",
    how="left"
)

# Merge Logon Feature
features = features.join(
    logon_feature,
    on="user",
    how="left"
)

# Merge Psychometric Feature
features = features.join(
    psychometric_feature,
    on="user",
    how="left"
)
features = features.fill_null(0)

print("Datasets Loaded Successfully\n")

print("Device:", device.shape)
print("Email:", email.shape)
print("File:", file.shape)
print("HTTP:", http.shape)
print("Logon:", logon.shape)
print("Psychometric:", psychometric.shape)

print(device_feature.head())
print("\nEmail Feature")
print(email_feature.head())
print("\nFile Feature")
print(file_feature.head())
print("\nHTTP Feature")
print(http_feature.head())
print("\nLogon Feature")
print(logon_feature.head())
print("\nPsychometric Feature")
print(psychometric_feature.head())
print("\nMerged Device + Email")
print(features.head())
print("\n========== FINAL FEATURE DATASET ==========\n")
print(features.shape)
print(features.head())
# ----------------------------------
# Save Final Feature Dataset
# ----------------------------------

OUTPUT_PATH = PROJECT_ROOT / "datasets" / "processed"

features.write_csv(
    OUTPUT_PATH / "final_features.csv"
)

print("\nFinal dataset saved successfully!")
print(OUTPUT_PATH / "final_features.csv")