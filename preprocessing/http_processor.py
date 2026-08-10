"""
=========================================================
HTTP Processor
AI Insider Threat Detection System
---------------------------------------------------------
Processes:
    dataset/raw/http.csv

Updates:
    FeatureAggregator

Features:
    - website_visit_count
    - unique_domain_count
    - avg_daily_web_activity
=========================================================
"""

import pandas as pd

from urllib.parse import urlparse

from dataset_config import HTTP_FILE
from aggregator import FeatureAggregator


CHUNK_SIZE = 100000


class HttpProcessor:

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

        chunk["url"] = chunk["url"].fillna("")

        return chunk

    # --------------------------------------------------

    @staticmethod
    def extract_domain(url):

        try:

            parsed = urlparse(url)

            return parsed.netloc.lower()

        except:

            return ""

    # --------------------------------------------------

    def process_chunk(self, chunk):

        chunk["domain"] = (

            chunk["url"]

            .apply(self.extract_domain)

        )

        grouped = chunk.groupby("user")

        for user, user_df in grouped:

            employee = self.aggregator.get(user)

            # ---------------------------------------
            # Total Website Visits
            # ---------------------------------------

            employee["website_visit_count"] += len(user_df)

            # ---------------------------------------
            # Unique Domains
            # ---------------------------------------

            domains = user_df["domain"].dropna().unique()

            employee["_domains"].update(domains)

            # ---------------------------------------
            # Daily Activity
            # ---------------------------------------

            daily_counts = user_df.groupby("day").size()

            for day, count in daily_counts.items():

                employee["_daily_web"][day] += int(count)

    # --------------------------------------------------

    def run(self):

        print()

        print("=" * 60)
        print("Processing HTTP Activity")
        print("=" * 60)

        chunk_number = 1

        for chunk in pd.read_csv(

            HTTP_FILE,

            chunksize=CHUNK_SIZE,

            low_memory=False

        ):

            print(f"Chunk {chunk_number}")

            chunk = self.preprocess_chunk(chunk)

            self.process_chunk(chunk)

            chunk_number += 1

        print()

        print("HTTP Processing Complete")