import pandas as pd
from pathlib import Path

RAW_DATA = Path("dataset/raw")
PROCESSED_DATA = Path("dataset/processed")

# Create processed folder if it doesn't exist
PROCESSED_DATA.mkdir(exist_ok=True)

print("=" * 50)
print("INSIDER THREAT DATA PREPROCESSING")
print("=" * 50)

print(f"Raw Dataset Exists      : {RAW_DATA.exists()}")
print(f"Processed Folder Exists : {PROCESSED_DATA.exists()}")

print("\nFiles inside Raw Dataset:\n")

for file in RAW_DATA.iterdir():
    print(file.name)

print("\nLoading logon.csv...")

logon_df = pd.read_csv(RAW_DATA / "logon.csv")

print("\nFirst 5 rows:\n")
print(logon_df.head())

print("\nDataset Shape:")
print(logon_df.shape)

print("\nColumn Names:")
print(logon_df.columns.tolist())

print("\nDataset Information:")
print(logon_df.info())

print("\nChecking for duplicate rows...")

duplicates = logon_df.duplicated().sum()

print(f"Duplicate rows: {duplicates}")

print("\nConverting date column to datetime...")

logon_df["date"] = pd.to_datetime(
    logon_df["date"],
    format="%m/%d/%Y %H:%M:%S"
)

print("Done!")

print("\nColumn Data Types:")
print(logon_df.dtypes)

print("\nCreating time-based features...")

logon_df["year"] = logon_df["date"].dt.year
logon_df["month"] = logon_df["date"].dt.month
logon_df["day"] = logon_df["date"].dt.day
logon_df["hour"] = logon_df["date"].dt.hour
logon_df["day_of_week"] = logon_df["date"].dt.day_name()

print("Time features created successfully!")

print("\nUpdated Dataset:")
print(logon_df.head())

print("\nUpdated Columns:")
print(logon_df.columns.tolist())

print("\nSaving processed dataset...")

processed_file = PROCESSED_DATA / "logon_processed.csv"

logon_df.to_csv(processed_file, index=False)

print(f"Dataset saved successfully to: {processed_file}")