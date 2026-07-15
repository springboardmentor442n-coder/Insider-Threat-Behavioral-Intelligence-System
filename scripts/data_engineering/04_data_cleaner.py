"""
===============================================================================
Module        : Dataset Cleaner
File          : 04_data_cleaner.py
Project       : Insider Threat Behavioral Intelligence System

Description:
    Cleans and standardizes all CERT datasets before integration.

Outputs:
    datasets/processed/

Author:
    Nandan Kabra
===============================================================================
"""

from pathlib import Path
import logging

import duckdb
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DATASET = PROJECT_ROOT / "datasets" / "raw" / "r4.2"

OUTPUT_DIR = PROJECT_ROOT / "datasets" / "processed"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

DATASETS = [
    "device",
    "email",
    "file",
    "logon",
    "psychometric"
]

class DatasetCleaner:

    def __init__(self):

        self.cleaned = {}

    def clean_dataset(self, dataset_name):

        logger.info("=" * 80)
        logger.info(f"Cleaning {dataset_name}.csv")
        logger.info("=" * 80)

        file_path = RAW_DATASET / f"{dataset_name}.csv"

        if dataset_name == "psychometric":

            df = duckdb.sql(f"""
            SELECT *
            FROM read_csv_auto(
                '{file_path.as_posix()}'
            )
            """).df()

        else:

            df = duckdb.sql(f"""
            SELECT *
            FROM read_csv_auto(
                '{file_path.as_posix()}',
                types={{'date':'VARCHAR'}}
            )
            """).df()

        logger.info(f"Rows Loaded : {len(df):,}")

                # Remove duplicate rows
        before = len(df)

        df = df.drop_duplicates()

        logger.info(
            f"Duplicates Removed : {before - len(df)}"
        )

        # Standardize column names
        df.columns = [
            c.strip().lower()
            for c in df.columns
        ]

        # Remove leading/trailing spaces
        object_cols = df.select_dtypes(include="object").columns

        for col in object_cols:

            df[col] = df[col].astype(str).str.strip()

        # Convert date column if present
        if "date" in df.columns:

            df["date"] = pd.to_datetime(
            df["date"],
            format="%m/%d/%Y %H:%M:%S",
            errors="coerce"
            )

        logger.info("Basic Cleaning Completed")

        output_file = OUTPUT_DIR / f"{dataset_name}.parquet"

        df.to_parquet(
            output_file,
            index=False
        )

        logger.info(
            f"Saved : {output_file}"
        )

        self.cleaned[dataset_name] = len(df)
    def run(self):
        for dataset in DATASETS:
            self.clean_dataset(dataset)

    def summary(self):
        logger.info("=" * 80)
        logger.info("SUMMARY")
        logger.info("=" * 80)

        for dataset, rows in self.cleaned.items():

            logger.info(
                f"{dataset:<15} {rows:,} rows"
            )

        logger.info("=" * 80)

def main():
    cleaner = DatasetCleaner()
    cleaner.run()
    cleaner.summary()

if __name__ == "__main__":
    main()
