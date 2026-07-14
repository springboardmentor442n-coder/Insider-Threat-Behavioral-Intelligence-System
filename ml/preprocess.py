import pandas as pd

# Load raw logon dataset
df = pd.read_csv("dataset/raw/logon.csv")

# Convert date column to datetime
df["date"] = pd.to_datetime(df["date"])

# Extract useful features
df["hour"] = df["date"].dt.hour
df["day"] = df["date"].dt.day_name()

# Weekend feature
df["is_weekend"] = df["day"].isin(["Saturday", "Sunday"]).astype(int)

# Keep only login events
df = df[df["activity"] == "Logon"]

# Save processed dataset
output_path = "dataset/processed/logon_processed.csv"
df.to_csv(output_path, index=False)

print("Processed dataset saved successfully!")
print(df.head())