"""
clean_data.py

Cleans the CERT datasets before feature engineering.
"""

from pathlib import Path
import polars as pl

from load_data import load_all_data

# Project Paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_PATH = PROJECT_ROOT / "datasets" / "processed"

# Create processed folder if it doesn't exist
PROCESSED_PATH.mkdir(parents=True, exist_ok=True)


def clean_dataset(df: pl.DataFrame) -> pl.DataFrame:
    """
    Basic cleaning operations.
    """

    # Remove duplicate rows
    df = df.unique()

    # Identify the user column to check for nulls
    columns = df.collect_schema().names()
    subset = []
    if "user" in columns:
        subset.append("user")
    if "user_id" in columns:
        subset.append("user_id")

    # Remove rows containing null values only in critical columns
    if subset:
        df = df.drop_nulls(subset=subset)

    return df


def clean_all():

    datasets = load_all_data()

    print("\n========== DATA CLEANING ==========\n")

    for name, df in datasets.items():

        print(f"Cleaning {name} dataset...")

        original_rows = df.height

        cleaned_df = clean_dataset(df)

        cleaned_rows = cleaned_df.height

        print(f"Original Rows : {original_rows}")
        print(f"Cleaned Rows  : {cleaned_rows}")

        output_file = PROCESSED_PATH / f"{name}_cleaned.csv"

        cleaned_df.write_csv(output_file)

        print(f"Saved -> {output_file}\n")


if __name__ == "__main__":
    clean_all()