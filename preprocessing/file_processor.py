"""
=========================================================
File Processor
AI Insider Threat Detection System
---------------------------------------------------------
Processes:
    dataset/raw/file.csv

Updates:
    FeatureAggregator

Features:
    - file_copy_count
    - avg_daily_file_copy
    - max_daily_file_copy
=========================================================
"""

import pandas as pd

from dataset_config import FILE_FILE
from aggregator import FeatureAggregator


CHUNK_SIZE = 100000


class FileProcessor:

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

        chunk["date"] = pd.to_datetime(

            chunk["date"],

            errors="coerce"

        )

        chunk["day"] = chunk["date"].dt.date

        return chunk

    # --------------------------------------------------

    def process_chunk(self, chunk):

        grouped = chunk.groupby("user")

        for user, user_df in grouped:

            employee = self.aggregator.get(user)

            # ---------------------------------------
            # Total File Copies
            # ---------------------------------------

            total_files = len(user_df)

            employee["file_copy_count"] += int(total_files)

            # ---------------------------------------
            # Daily File Copies
            # ---------------------------------------

            daily_counts = user_df.groupby("day").size()

            for day, count in daily_counts.items():

                employee["_daily_file_copy"][day] += int(count)

    # --------------------------------------------------

    def run(self):

        print()

        print("=" * 60)
        print("Processing File Activity")
        print("=" * 60)

        chunk_number = 1

        for chunk in pd.read_csv(

            FILE_FILE,

            chunksize=CHUNK_SIZE,

            low_memory=False

        ):

            print(f"Chunk {chunk_number}")

            chunk = self.preprocess_chunk(chunk)

            self.process_chunk(chunk)

            chunk_number += 1

        print()

        print("File Processing Complete")