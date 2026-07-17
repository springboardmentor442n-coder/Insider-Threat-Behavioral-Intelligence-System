import pandas as pd
from pathlib import Path


def generate_features(input_file, output_file):
    print("=" * 50)
    print("FEATURE ENGINEERING")
    print("=" * 50)

    print("\nLoading processed dataset...")

    df = pd.read_csv(input_file)

    print("Dataset Loaded Successfully!")

    # Login count for each user
    user_login_count = (
        df.groupby("user")
          .size()
          .reset_index(name="login_count")
    )

    df = df.merge(user_login_count, on="user")

    # Number of unique PCs used by each user
    user_pc_count = (
        df.groupby("user")["pc"]
          .nunique()
          .reset_index(name="unique_pc_count")
    )

    df = df.merge(user_pc_count, on="user")

    # Weekend feature
    df["is_weekend"] = df["day"].isin(
        ["Saturday", "Sunday"]
    ).astype(int)

    # Late night login feature
    df["late_night_login"] = (
        (df["hour"] >= 22) |
        (df["hour"] <= 5)
    ).astype(int)

    # Create output folder if needed
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)

    # Save engineered dataset
    df.to_csv(output_file, index=False)

    print(f"\nFeature engineered dataset saved to {output_file}")

    return output_file