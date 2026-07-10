import pandas as pd
from pathlib import Path

PROCESSED_DATA = Path("dataset/processed")

print("Loading feature engineered dataset...")

df = pd.read_csv(PROCESSED_DATA / "logon_features.csv")

print(df.head())
print(df.shape)
print("\nCreating target labels...")

df["target"] = (
    (df["late_night_login"] == 1) |
    (df["unique_pc_count"] > 3)
).astype(int)

print(df["target"].value_counts())
labeled_file = PROCESSED_DATA / "logon_labeled.csv"

df.to_csv(labeled_file, index=False)

print("Labeled dataset saved!")