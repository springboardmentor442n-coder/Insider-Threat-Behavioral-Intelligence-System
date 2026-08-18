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

# ---------------------------------
# Merge Feature Tables
# ---------------------------------

# Use psychometric_feature as the population base to ensure no users are dropped
features = psychometric_feature

# Merge Device Feature
features = features.join(
    device_feature,
    on="user",
    how="left"
)

# Merge Email Feature
features = features.join(
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

# Fill nulls with 0 ONLY for activity count features (not psychometric data)
activity_cols = [
    "device_connections",
    "emails_sent",
    "files_accessed",
    "websites_visited",
    "logon_count"
]

features = features.with_columns([
    pl.col(c).fill_null(0) for c in activity_cols
])

# Enforce exact column order required for the model
final_cols = [
    "user",
    "device_connections",
    "emails_sent",
    "files_accessed",
    "websites_visited",
    "logon_count",
    "O",
    "C",
    "E",
    "A",
    "N"
]
features = features.select(final_cols)

print("Datasets Loaded Successfully\n")

print("Device:", device.shape)
print("Email:", email.shape)
print("File:", file.shape)
print("HTTP:", http.shape)
print("Logon:", logon.shape)
print("Psychometric:", psychometric.shape)
# ----------------------------------
# Save Final Feature Dataset
# ----------------------------------

OUTPUT_PATH = PROJECT_ROOT / "datasets" / "processed"

features.write_csv(
    OUTPUT_PATH / "final_features.csv"
)

print("\nFinal dataset saved successfully!")
print(OUTPUT_PATH / "final_features.csv")