"""
=========================================================
LDAP Processor
AI Insider Threat Detection System
---------------------------------------------------------
Processes:
    LDAP/

Updates:
    FeatureAggregator

Features:
    Department
    Role
    Business Unit
=========================================================
"""

import os
import pandas as pd

from dataset_config import LDAP_FOLDER
from aggregator import FeatureAggregator


class LDAPProcessor:

    def __init__(self, aggregator: FeatureAggregator):

        self.aggregator = aggregator

    # --------------------------------------------------

    def run(self):

       print()
       print("=" * 60)
       print("Processing LDAP Data")
       print("=" * 60)

       files = [f for f in os.listdir(LDAP_FOLDER) if f.endswith(".csv")]

       for file in files:

           path = os.path.join(LDAP_FOLDER, file)

           df = pd.read_csv(path, low_memory=False)

        # Remove hidden spaces from column names
           df.columns = df.columns.str.strip()

           df["user_id"] = (
            df["user_id"]
            .astype(str)
            .str.upper()
            .str.strip()
        )

           for _, row in df.iterrows():

               employee = self.aggregator.get(row["user_id"])

               employee["department"] = (
                row["department"]
                if pd.notna(row["department"])
                else "Unknown"
            )

               employee["role"] = (
                row["role"]
                if pd.notna(row["role"])
                else "Unknown"
            )

               employee["business_unit"] = (
                row["business_unit"]
                if pd.notna(row["business_unit"])
                else "Unknown"
            )

       print()
       print("LDAP Processing Complete")