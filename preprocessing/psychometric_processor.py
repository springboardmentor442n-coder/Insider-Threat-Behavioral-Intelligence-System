"""
=========================================================
Psychometric Processor
AI Insider Threat Detection System
---------------------------------------------------------
Processes:
    psychometric.csv

Updates:
    FeatureAggregator

Features:
    O
    C
    E
    A
    N
=========================================================
"""

import pandas as pd

from dataset_config import PSYCHOMETRIC_FILE
from aggregator import FeatureAggregator


class PsychometricProcessor:

    def __init__(self, aggregator: FeatureAggregator):

        self.aggregator = aggregator

    # --------------------------------------------------

    def run(self):

        print()

        print("=" * 60)
        print("Processing Psychometric Data")
        print("=" * 60)

        df = pd.read_csv(

            PSYCHOMETRIC_FILE,

            low_memory=False

        )

        df["user_id"] = (

            df["user_id"]

            .astype(str)

            .str.upper()

            .str.strip()

        )

        for _, row in df.iterrows():

            employee = self.aggregator.get(

                row["user_id"]

            )

            employee["O"] = float(row["O"])

            employee["C"] = float(row["C"])

            employee["E"] = float(row["E"])

            employee["A"] = float(row["A"])

            employee["N"] = float(row["N"])

        print()

        print("Psychometric Processing Complete")