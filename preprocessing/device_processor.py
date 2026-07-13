"""
=========================================================
Device Processor
AI Insider Threat Detection System
---------------------------------------------------------
Processes:
    dataset/raw/device.csv

Updates:
    FeatureAggregator
=========================================================
"""

import pandas as pd

from dataset_config import DEVICE_FILE
from aggregator import FeatureAggregator


CHUNK_SIZE = 100000


class DeviceProcessor:

    def __init__(self, aggregator: FeatureAggregator):

        self.aggregator = aggregator

    # --------------------------------------------------

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

        return chunk

    # --------------------------------------------------

    def process_chunk(self, chunk):

        grouped = chunk.groupby("user")

        for user, user_df in grouped:

            employee = self.aggregator.get(user)

            connect = (

                user_df["activity"]

                .str.contains("connect", case=False, na=False)

            ).sum()

            disconnect = (

                user_df["activity"]

                .str.contains("disconnect", case=False, na=False)

            ).sum()

            employee["usb_connect_count"] += int(connect)

            employee["usb_disconnect_count"] += int(disconnect)

    # --------------------------------------------------

    def run(self):

        print()

        print("=" * 60)
        print("Processing Device Activity")
        print("=" * 60)

        chunk_number = 1

        for chunk in pd.read_csv(

            DEVICE_FILE,

            chunksize=CHUNK_SIZE,

            low_memory=False

        ):

            print(f"Chunk {chunk_number}")

            chunk = self.preprocess_chunk(chunk)

            self.process_chunk(chunk)

            chunk_number += 1

        print()

        print("Device Processing Complete")