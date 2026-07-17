import pandas as pd
from pathlib import Path


def preprocess_logon(input_file, output_file):
    # Load dataset
    df = pd.read_csv(input_file)

    # Convert date column to datetime
    df["date"] = pd.to_datetime(df["date"])

    # Extract features
    df["hour"] = df["date"].dt.hour
    df["day"] = df["date"].dt.day_name()

    # Weekend feature
    df["is_weekend"] = df["day"].isin(["Saturday", "Sunday"]).astype(int)

    # Keep only login events
    df = df[df["activity"] == "Logon"]

    # Create output folder if needed
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)

    # Save processed file
    df.to_csv(output_file, index=False)

    print(f"Processed dataset saved to {output_file}")

    return output_file