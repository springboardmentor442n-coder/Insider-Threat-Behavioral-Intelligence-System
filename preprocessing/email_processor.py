"""
=========================================================
Email Processor
=========================================================
"""

import pandas as pd

from dataset_config import EMAIL_FILE
from aggregator import FeatureAggregator

CHUNK_SIZE = 100000


class EmailProcessor:

    def __init__(self, aggregator: FeatureAggregator):
        self.aggregator = aggregator

    @staticmethod
    def preprocess_chunk(chunk):

        chunk["user"] = (
            chunk["user"]
            .astype(str)
            .str.upper()
            .str.strip()
        )

        chunk["attachments"] = pd.to_numeric(
            chunk["attachments"],
            errors="coerce"
        ).fillna(0)

        chunk["size"] = pd.to_numeric(
            chunk["size"],
            errors="coerce"
        ).fillna(0)

        for col in ["to", "cc", "bcc"]:
            chunk[col] = chunk[col].fillna("").astype(str)

        return chunk

    @staticmethod
    def is_external(address):

        if not address:
            return False

        address = address.lower()

        return "@dtaa.com" not in address

    def process_chunk(self, chunk):

        grouped = chunk.groupby("user")

        for user, user_df in grouped:

            employee = self.aggregator.get(user)

            employee["email_sent_count"] += len(user_df)

            employee["_attachment_sum"] += user_df["attachments"].sum()

            employee["_email_size_sum"] += user_df["size"].sum()

            external = 0

            for _, row in user_df.iterrows():

                recipients = []

                for col in ["to", "cc", "bcc"]:

                    value = row[col]

                    if value:

                        recipients.extend(value.split(";"))

                if any(self.is_external(x.strip()) for x in recipients):
                    external += 1

            employee["external_email_count"] += external

    def run(self):

        print("\n" + "=" * 60)
        print("Processing Email Activity")
        print("=" * 60)

        chunk_no = 1

        for chunk in pd.read_csv(
            EMAIL_FILE,
            chunksize=CHUNK_SIZE,
            low_memory=False
        ):

            print(f"Chunk {chunk_no}")

            chunk = self.preprocess_chunk(chunk)

            self.process_chunk(chunk)

            chunk_no += 1

        print("\nEmail Processing Complete")