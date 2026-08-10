"""
=========================================================
Login Processor
AI Insider Threat Detection System
---------------------------------------------------------
Processes:
    dataset/raw/logon.csv

Updates:
    FeatureAggregator
=========================================================
"""

import pandas as pd

from dataset_config import LOGON_FILE
from aggregator import FeatureAggregator

CHUNK_SIZE = 100000


class LoginProcessor:

    def __init__(self, aggregator: FeatureAggregator):

        self.aggregator = aggregator

    # ----------------------------------------------------

    @staticmethod
    def preprocess_chunk(chunk):

        chunk["user"] = (

            chunk["user"]

            .astype(str)

            .str.upper()

            .str.strip()

        )

        chunk["activity"] = (

            chunk["activity"]

            .astype(str)

            .str.lower()

        )

        chunk["date"] = pd.to_datetime(

            chunk["date"],

            errors="coerce"

        )

        chunk["hour"] = chunk["date"].dt.hour

        chunk["weekday"] = chunk["date"].dt.dayofweek

        return chunk

    # ----------------------------------------------------

    def process_chunk(self, chunk):

        users = chunk["user"].unique()

        for user in users:

            employee = self.aggregator.get(user)

            user_df = chunk[chunk["user"] == user]

            # -----------------------------
            # Login Count
            # -----------------------------

            logins = user_df[
                user_df["activity"] == "logon"
            ]

            employee["login_count"] += len(logins)

            # -----------------------------
            # Logoff Count
            # -----------------------------

            logoffs = user_df[
                user_df["activity"] == "logoff"
            ]

            employee["logoff_count"] += len(logoffs)

            # -----------------------------
            # Night Logins
            # -----------------------------

            employee["night_login_count"] += len(

                logins[

                    (logins["hour"] < 6)

                    |

                    (logins["hour"] >= 20)

                ]

            )

            # -----------------------------
            # Weekend Logins
            # -----------------------------

            employee["weekend_login_count"] += len(

                logins[

                    logins["weekday"] >= 5

                ]

            )

            # -----------------------------
            # Unique PCs
            # -----------------------------

            employee["_pc_set"].update(

                user_df["pc"].dropna().unique()

            )

    # ----------------------------------------------------

    def run(self):

        print()

        print("=" * 60)

        print("Processing Login Activity")

        print("=" * 60)

        chunk_no = 1

        for chunk in pd.read_csv(

            LOGON_FILE,

            chunksize=CHUNK_SIZE,

            low_memory=False

        ):

            print(f"Chunk {chunk_no}")

            chunk = self.preprocess_chunk(chunk)

            self.process_chunk(chunk)

            chunk_no += 1

        print()

        print("Login Processing Complete")