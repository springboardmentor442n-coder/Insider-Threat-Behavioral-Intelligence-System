"""
load_data.py

Loads all raw datasets required for the Insider Threat Behavioral
Intelligence System.
"""

from pathlib import Path
import polars as pl

# Project Root
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Raw Dataset Folder
DATASET_PATH = PROJECT_ROOT / "datasets" / "raw"

# Dataset Files
FILES = {
    "device": "device.csv",
    "email": "email.csv",
    "file": "file.csv",
    "http": "http.csv",
    "logon": "logon.csv",
    "psychometric": "psychometric.csv"
}


def load_all_data():
    """
    Load all datasets into a dictionary.
    """

    datasets = {}

    for name, filename in FILES.items():

        filepath = DATASET_PATH / filename

        print(f"Loading {filename}...")

        datasets[name] = pl.read_csv(filepath)

        print(f"{name} loaded successfully.")

    return datasets


if __name__ == "__main__":

    data = load_all_data()

    print("\nDatasets Loaded:\n")

    for name, df in data.items():
        print(f"{name} -> {df.shape}")