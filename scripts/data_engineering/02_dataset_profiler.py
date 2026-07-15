"""
===============================================================================
Module        : Dataset Profiler
File          : 02_dataset_profiler.py
Project       : Insider Threat Behavioral Intelligence System

Description:
    Profiles every CSV dataset discovered by the Dataset Inventory Engine.
    Generates detailed statistics for each dataset.

Outputs:
    datasets/profiling/profiles/
        ├── device_profile.json
        ├── email_profile.json
        ├── ...
        └── summary.json

Author:
    Nandan Kabra
===============================================================================
"""

from pathlib import Path
from datetime import datetime
import json
import logging

import pandas as pd

# =============================================================================
# Logging Configuration
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

# =============================================================================
# Project Paths
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DATASET = PROJECT_ROOT / "datasets" / "raw" / "r4.2"

PROFILE_ROOT = PROJECT_ROOT / "datasets" / "profiling"

PROFILE_DIR = PROFILE_ROOT / "profiles"

PROFILE_DIR.mkdir(parents=True, exist_ok=True)

INVENTORY_JSON = PROFILE_ROOT / "dataset_inventory.json"


# =============================================================================
# Dataset Profiler
# =============================================================================

class DatasetProfiler:

    LARGE_FILE_THRESHOLD_MB = 200
    CHUNK_SIZE = 100000

    def __init__(self):

        self.inventory = []
        self.summary = []

    # -------------------------------------------------------------------------

    def load_inventory(self):

        logger.info("=" * 80)
        logger.info("LOADING INVENTORY")
        logger.info("=" * 80)

        if not INVENTORY_JSON.exists():

            raise FileNotFoundError(
                "dataset_inventory.json not found.\n"
                "Run 01_dataset_inventory.py first."
            )

        with open(INVENTORY_JSON, "r", encoding="utf-8") as f:

            self.inventory = json.load(f)

        logger.info(f"Datasets Loaded : {len(self.inventory)}")

    # -------------------------------------------------------------------------

    def profile_all(self):

        logger.info("\nStarting Dataset Profiling...\n")

        for dataset in self.inventory:

            if "Error" in dataset:
                continue

            relative_path = dataset["Relative Path"]

            file_path = RAW_DATASET / relative_path

            logger.info(f"Profiling : {relative_path}")

            profile = self.profile_file(file_path)

            output_name = (
                relative_path.replace("\\", "_")
                .replace("/", "_")
                .replace(".csv", "_profile.json")
            )

            with open(
                PROFILE_DIR / output_name,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(profile, f, indent=4, default=str)

            self.summary.append({

                "File": dataset["File Name"],

                "Rows": profile["rows"],

                "Columns": profile["columns"],

                "Missing Values": profile["missing_values_total"],

                "Duplicate Rows": profile["duplicate_rows"]

            })

        logger.info("\nDataset Profiling Completed.")
            # -------------------------------------------------------------------------

    def profile_file(self, file_path: Path):

        file_size_mb = file_path.stat().st_size / (1024 * 1024)

        if file_size_mb > self.LARGE_FILE_THRESHOLD_MB:

            logger.info(
                f"Large file detected ({round(file_size_mb,2)} MB). "
                f"Using chunk processing..."
            )

            return self.profile_large_file(file_path)

        logger.info("Using full dataframe profiling...")

        df = pd.read_csv(file_path)

        profile = {

            "file_name": file_path.name,

            "file_size_mb": round(file_size_mb, 2),

            "rows": len(df),

            "columns": len(df.columns),

            "column_names": list(df.columns),

            "column_types": {
                col: str(dtype)
                for col, dtype in df.dtypes.items()
            },

            "memory_usage_mb":
                round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2),

            "missing_values": df.isnull().sum().to_dict(),

            "missing_values_total":
                int(df.isnull().sum().sum()),

            "duplicate_rows":
                int(df.duplicated().sum()),

            "unique_values": {
                col: int(df[col].nunique())
                for col in df.columns
            },

            "sample_records":
                df.head(5).to_dict(orient="records")

        }

        # -------------------------------------------------------------
        # Date Information
        # -------------------------------------------------------------

        if "date" in df.columns:

            try:

                dates = pd.to_datetime(
                    df["date"],
                    errors="coerce"
                )

                profile["date_range"] = {

                    "start": str(dates.min()),

                    "end": str(dates.max())

                }

            except Exception:

                profile["date_range"] = None

        # -------------------------------------------------------------
        # User Statistics
        # -------------------------------------------------------------

        if "user" in df.columns:

            profile["unique_users"] = int(
                df["user"].nunique()
            )

        # -------------------------------------------------------------
        # PC Statistics
        # -------------------------------------------------------------

        if "pc" in df.columns:

            profile["unique_pcs"] = int(
                df["pc"].nunique()
            )

        return profile

    # -------------------------------------------------------------------------

    def profile_large_file(self, file_path: Path):

        total_rows = 0

        total_missing = {}

        column_types = {}

        unique_users = set()

        unique_pcs = set()

        sample_records = []

        duplicate_rows = 0

        column_names = None

        memory_usage = 0

        min_date = None

        max_date = None

        for chunk in pd.read_csv(
            file_path,
            chunksize=self.CHUNK_SIZE
        ):

            total_rows += len(chunk)

            memory_usage += chunk.memory_usage(
                deep=True
            ).sum()

            if column_names is None:

                column_names = list(chunk.columns)

                column_types = {
                    c: str(t)
                    for c, t in chunk.dtypes.items()
                }

            missing = chunk.isnull().sum()

            for col in missing.index:

                total_missing[col] = (
                    total_missing.get(col, 0)
                    + int(missing[col])
                )

            duplicate_rows += int(
                chunk.duplicated().sum()
            )

            if "user" in chunk.columns:

                unique_users.update(
                    chunk["user"].dropna().unique()
                )

            if "pc" in chunk.columns:

                unique_pcs.update(
                    chunk["pc"].dropna().unique()
                )

            if "date" in chunk.columns:

                dates = pd.to_datetime(
                    chunk["date"],
                    errors="coerce"
                )

                chunk_min = dates.min()

                chunk_max = dates.max()

                if (
                    min_date is None
                    or chunk_min < min_date
                ):
                    min_date = chunk_min

                if (
                    max_date is None
                    or chunk_max > max_date
                ):
                    max_date = chunk_max

            if len(sample_records) < 5:

                sample_records.extend(
                    chunk.head(5).to_dict(
                        orient="records"
                    )
                )

        profile = {

            "file_name": file_path.name,

            "file_size_mb":
                round(file_path.stat().st_size / (1024 * 1024), 2),

            "rows": total_rows,

            "columns": len(column_names),

            "column_names": column_names,

            "column_types": column_types,

            "memory_usage_mb":
                round(memory_usage / (1024 * 1024), 2),

            "missing_values": total_missing,

            "missing_values_total":
                sum(total_missing.values()),

            "duplicate_rows": duplicate_rows,

            "unique_users": len(unique_users),

            "unique_pcs": len(unique_pcs),

            "date_range": {

                "start": str(min_date),

                "end": str(max_date)

            },

            "sample_records": sample_records[:5]

        }

        return profile
