"""
===============================================================================
Module        : Dataset Inventory Engine
File          : 01_dataset_inventory.py
Project       : Insider Threat Behavioral Intelligence System

Description:
    Recursively scans the CERT Insider Threat Dataset and generates a complete
    inventory of all CSV files.

Outputs:
    datasets/profiling/
        ├── dataset_inventory.csv
        ├── dataset_inventory.json
        └── dataset_inventory.md

Author:
    Nandan Kabra
===============================================================================
"""

from pathlib import Path
from datetime import datetime
import logging
import json
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

PROFILE_OUTPUT = PROJECT_ROOT / "datasets" / "profiling"

PROFILE_OUTPUT.mkdir(parents=True, exist_ok=True)


# =============================================================================
# Dataset Inventory Engine
# =============================================================================

class DatasetInventoryEngine:

    def __init__(self, dataset_path: Path):

        self.dataset_path = dataset_path
        self.inventory = []

    # -------------------------------------------------------------------------

    def discover_files(self):

        logger.info("=" * 80)
        logger.info("CERT DATASET INVENTORY ENGINE")
        logger.info("=" * 80)

        if not self.dataset_path.exists():

            logger.error("Dataset folder not found.")
            return

        csv_files = sorted(self.dataset_path.rglob("*.csv"))

        logger.info(f"Dataset : {self.dataset_path}")
        logger.info(f"CSV Files Found : {len(csv_files)}\n")

        for csv_file in csv_files:

            logger.info(f"Scanning : {csv_file.relative_to(self.dataset_path)}")

            metadata = self.analyze_file(csv_file)

            self.inventory.append(metadata)

        logger.info("\nInventory collection completed.")

    # -------------------------------------------------------------------------

    def analyze_file(self, file_path: Path):

        logger.info("Reading metadata...")

        try:

            # Read only header
            header = pd.read_csv(file_path, nrows=0)

            # Count rows efficiently
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                row_count = sum(1 for _ in f) - 1

            size_mb = round(file_path.stat().st_size / (1024 * 1024), 2)

            modified = datetime.fromtimestamp(
                file_path.stat().st_mtime
            ).strftime("%Y-%m-%d %H:%M:%S")

            columns = list(header.columns)

            metadata = {

                "File Name": file_path.name,

                "Relative Path": str(file_path.relative_to(self.dataset_path)),

                "Rows": row_count,

                "Columns": len(columns),

                "Column Names": ", ".join(columns),

                "File Size (MB)": size_mb,

                "Modified": modified,

                "Has User Column": "user" in [
                    c.lower() for c in columns
                ],

                "Has Date Column": "date" in [
                    c.lower() for c in columns
                ],

                "Has PC Column": "pc" in [
                    c.lower() for c in columns
                ]

            }

            return metadata

        except Exception as e:

            logger.error(f"Error processing {file_path.name}")

            logger.error(str(e))

            return {

                "File Name": file_path.name,

                "Relative Path": str(file_path.relative_to(self.dataset_path)),

                "Error": str(e)

            }

    # -------------------------------------------------------------------------

    def export_csv(self):

        df = pd.DataFrame(self.inventory)

        output = PROFILE_OUTPUT / "dataset_inventory.csv"

        df.to_csv(output, index=False)

        logger.info(f"CSV Inventory Saved : {output}")

    # -------------------------------------------------------------------------

    def export_json(self):

        output = PROFILE_OUTPUT / "dataset_inventory.json"

        with open(output, "w", encoding="utf-8") as f:

            json.dump(self.inventory, f, indent=4)

        logger.info(f"JSON Inventory Saved : {output}")

    # -------------------------------------------------------------------------

    def export_markdown(self):

        output = PROFILE_OUTPUT / "dataset_inventory.md"

        df = pd.DataFrame(self.inventory)

        with open(output, "w", encoding="utf-8") as f:

            f.write("# CERT Dataset Inventory\n\n")

            f.write(df.to_markdown(index=False))

        logger.info(f"Markdown Inventory Saved : {output}")

    # -------------------------------------------------------------------------

    def summary(self):

        logger.info("\n")

        logger.info("=" * 80)

        logger.info("SUMMARY")

        logger.info("=" * 80)

        logger.info(f"Files Processed : {len(self.inventory)}")

        total_size = sum(
            item.get("File Size (MB)", 0)
            for item in self.inventory
            if isinstance(item.get("File Size (MB)", 0), (int, float))
        )

        logger.info(f"Total Dataset Size : {round(total_size,2)} MB")

        logger.info("=" * 80)


# =============================================================================
# Main
# =============================================================================

def main():

    engine = DatasetInventoryEngine(RAW_DATASET)

    engine.discover_files()

    engine.export_csv()

    engine.export_json()

    engine.export_markdown()

    engine.summary()


# =============================================================================
# Entry Point
# =============================================================================

if __name__ == "__main__":

    main()
