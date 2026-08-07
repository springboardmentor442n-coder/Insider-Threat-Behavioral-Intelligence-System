import pandas as pd
from pathlib import Path
import random

# ----------------------------------------
# Project Paths
# ----------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_DATA_PATH = PROJECT_ROOT / "datasets" / "processed" / "final_features.csv"

# ----------------------------------------
# Stream Generator
# ----------------------------------------

def stream_data(csv_path=None):
    """
    Simulates real-time employee activity by yielding
    one random employee record at a time.
    """

    if csv_path is None:
        csv_path = DEFAULT_DATA_PATH

    df = pd.read_csv(csv_path)

    while True:
        row = df.sample(1).iloc[0]
        yield row