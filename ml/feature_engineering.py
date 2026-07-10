import pandas as pd
from pathlib import Path

PROCESSED_DATA = Path("dataset/processed")

file_path = PROCESSED_DATA / "logon_processed.csv"

print("Loading processed dataset...")

df = pd.read_csv(file_path)

print("Dataset Loaded Successfully!")

print(df.head())

print("\nDataset Shape:")
print(df.shape)

print("\nCalculating login count for each user...")

user_login_count = (
    df.groupby("user")
      .size()
      .reset_index(name="login_count")
)

print(user_login_count.head())

df = df.merge(user_login_count, on="user")

print("\nDataset after adding login_count:")

print(df.head())

engineered_file = PROCESSED_DATA / "logon_features.csv"

df.to_csv(engineered_file, index=False)

print("\nFeature engineered dataset saved!")