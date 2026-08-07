"""
merge_data.py

Creates one behavioral dataset from all cleaned CERT datasets.
"""

from pathlib import Path
import polars as pl

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROCESSED = PROJECT_ROOT / "datasets" / "processed"


def load_processed():

    datasets = {}

    datasets["device"] = pl.read_csv(PROCESSED / "device_cleaned.csv")
    datasets["email"] = pl.read_csv(PROCESSED / "email_cleaned.csv")
    datasets["file"] = pl.read_csv(PROCESSED / "file_cleaned.csv")
    datasets["http"] = pl.read_csv(PROCESSED / "http_cleaned.csv")
    datasets["logon"] = pl.read_csv(PROCESSED / "logon_cleaned.csv")
    datasets["psychometric"] = pl.read_csv(PROCESSED / "psychometric_cleaned.csv")

    return datasets


def show_information():

    data = load_processed()

    print("\n========== CLEAN DATA SUMMARY ==========\n")

    for name, df in data.items():

        print(f"{name}")

        print(f"Rows : {df.height}")

        print(f"Columns : {df.width}")

        print(df.columns)

        print("-" * 50)


if __name__ == "__main__":

    show_information()