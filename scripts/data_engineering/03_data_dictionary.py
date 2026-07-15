"""
===============================================================================
Module        : Data Dictionary Generator
File          : 03_data_dictionary.py
Project       : Insider Threat Behavioral Intelligence System

Description:
    Generates a complete Data Dictionary for every CERT dataset.

Outputs:
    datasets/profiling/

        data_dictionary.csv
        data_dictionary.json
        data_dictionary.md

Author:
    Nandan Kabra
===============================================================================
"""

from pathlib import Path
import json
import logging

import pandas as pd
import duckdb

# =============================================================================
# Logging
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

PROFILE_DIR = PROJECT_ROOT / "datasets" / "profiling"

INVENTORY_FILE = PROFILE_DIR / "dataset_inventory.json"

CSV_OUTPUT = PROFILE_DIR / "data_dictionary.csv"

JSON_OUTPUT = PROFILE_DIR / "data_dictionary.json"

MD_OUTPUT = PROFILE_DIR / "data_dictionary.md"

# =============================================================================
# Column Categories
# =============================================================================

COLUMN_CATEGORY = {

    "id": "Identifier",

    "date": "Timestamp",

    "user": "Employee",

    "employee_name": "Employee",

    "user_id": "Employee",

    "pc": "Computer",

    "activity": "Activity",

    "url": "Website",

    "filename": "File",

    "content": "Content",

    "to": "Email",

    "from": "Email",

    "cc": "Email",

    "bcc": "Email",

    "attachments": "Email",

    "size": "Metadata",

    "O": "Personality",

    "C": "Personality",

    "E": "Personality",

    "A": "Personality",

    "N": "Personality"

}

COLUMN_DESCRIPTION = {

    "id":
        "Unique Event Identifier",

    "date":
        "Timestamp of Event",

    "user":
        "Employee Identifier",

    "employee_name":
        "Employee Name",

    "user_id":
        "Employee Identifier",

    "pc":
        "Computer Name",

    "activity":
        "Type of Activity",

    "url":
        "Visited Website",

    "filename":
        "Accessed File",

    "content":
        "Associated Content",

    "to":
        "Email Recipient",

    "from":
        "Email Sender",

    "cc":
        "Carbon Copy",

    "bcc":
        "Blind Carbon Copy",

    "attachments":
        "Attachment Count",

    "size":
        "Object Size",

    "O":
        "Openness",

    "C":
        "Conscientiousness",

    "E":
        "Extraversion",

    "A":
        "Agreeableness",

    "N":
        "Neuroticism"

}

# =============================================================================
# Data Dictionary Generator
# =============================================================================

class DataDictionaryGenerator:

    def __init__(self):

        self.inventory = []

        self.dictionary = []

    def load_inventory(self):

        logger.info("=" * 80)

        logger.info("Loading Dataset Inventory")

        logger.info("=" * 80)

        with open(INVENTORY_FILE, "r", encoding="utf-8") as f:

            self.inventory = json.load(f)

        logger.info(
            f"Datasets Loaded : {len(self.inventory)}"
        )

    # =========================================================================
    # Generate Data Dictionary
    # =========================================================================

    def generate_dictionary(self):

        logger.info("=" * 80)
        logger.info("Generating Data Dictionary")
        logger.info("=" * 80)

        for dataset in self.inventory:

            if "Error" in dataset:
                continue

            relative_path = dataset["Relative Path"]

            dataset_name = Path(relative_path).stem

            file_path = RAW_DATASET / relative_path

            logger.info(f"Processing : {relative_path}")

            try:

                df = duckdb.sql(f"""
                    SELECT *
                    FROM read_csv_auto('{file_path.as_posix()}')
                    LIMIT 5
                """).df()

            except Exception as e:

                logger.error(f"Unable to read {relative_path}")

                logger.error(str(e))

                continue

            for column in df.columns:

                dtype = str(df[column].dtype)

                category = COLUMN_CATEGORY.get(
                    column,
                    "Other"
                )

                description = COLUMN_DESCRIPTION.get(
                    column,
                    "Description Not Available"
                )

                used_in_timeline = column.lower() in [
                    "date",
                    "user",
                    "pc",
                    "activity",
                    "url",
                    "filename",
                    "content"
                ]

                used_in_feature_engineering = column.lower() in [

                    "date",

                    "user",

                    "pc",

                    "activity",

                    "url",

                    "filename",

                    "content",

                    "employee_name",

                    "user_id",

                    "o",

                    "c",

                    "e",

                    "a",

                    "n"

                ]

                used_in_ml = column.lower() in [

                    "user",

                    "activity",

                    "url",

                    "filename",

                    "content",

                    "o",

                    "c",

                    "e",

                    "a",

                    "n"

                ]

                self.dictionary.append({

                    "Dataset": dataset_name,

                    "Column": column,

                    "Data Type": dtype,

                    "Category": category,

                    "Used In Timeline": "Yes" if used_in_timeline else "No",

                    "Used In Feature Engineering":
                        "Yes" if used_in_feature_engineering else "No",

                    "Used In Machine Learning":
                        "Yes" if used_in_ml else "No",

                    "Description": description

                })

        logger.info("Dictionary Generation Completed.")

            # =========================================================================
    # Export CSV
    # =========================================================================

    def export_csv(self):

        df = pd.DataFrame(self.dictionary)

        df.to_csv(

            CSV_OUTPUT,

            index=False

        )

        logger.info(f"CSV Saved : {CSV_OUTPUT}")

    # =========================================================================
    # Export JSON
    # =========================================================================

    def export_json(self):

        with open(

            JSON_OUTPUT,

            "w",

            encoding="utf-8"

        ) as f:

            json.dump(

                self.dictionary,

                f,

                indent=4,

                ensure_ascii=False

            )

        logger.info(f"JSON Saved : {JSON_OUTPUT}")

    # =========================================================================
    # Export Markdown
    # =========================================================================

    def export_markdown(self):

        df = pd.DataFrame(self.dictionary)

        with open(

            MD_OUTPUT,

            "w",

            encoding="utf-8"

        ) as f:

            f.write("# CERT Dataset Data Dictionary\n\n")

            f.write(df.to_markdown(index=False))

        logger.info(f"Markdown Saved : {MD_OUTPUT}")

            # =========================================================================
    # Summary
    # =========================================================================

    def summary(self):

        logger.info("=" * 80)

        logger.info("SUMMARY")

        logger.info("=" * 80)

        logger.info(f"Datasets Processed : {len(self.inventory)}")

        logger.info(f"Columns Documented : {len(self.dictionary)}")

        logger.info("=" * 80)


# =============================================================================
# Main
# =============================================================================

def main():

    generator = DataDictionaryGenerator()

    generator.load_inventory()

    generator.generate_dictionary()

    generator.export_csv()

    generator.export_json()

    generator.export_markdown()

    generator.summary()


if __name__ == "__main__":

    main()
