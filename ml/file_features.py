import pandas as pd


class FileFeatureExtractor:

    def __init__(self):
        self.features = []

    def process_chunk(self, chunk):

        # Convert timestamp
        chunk["date"] = pd.to_datetime(
            chunk["date"],
            errors="coerce"
        )

        chunk["hour"] = chunk["date"].dt.hour

        # Employee ID
        chunk["employee_id"] = chunk["user"]

        # Weekend flag
        chunk["is_weekend"] = (
            chunk["date"].dt.dayofweek >= 5
        ).astype(int)

        grouped = (
            chunk.groupby("employee_id")
            .agg(
                file_access_count=("employee_id", "size"),
                unique_files=("filename", "nunique"),
                after_hours_file_access=(
                    "hour",
                    lambda x: ((x < 8) | (x > 18)).sum()
                ),
                weekend_file_access=("is_weekend", "sum"),
                latest_file_timestamp=("date", "max")
            )
            .reset_index()
        )

        self.features.append(grouped)

    def finalize(self):

        if not self.features:
            return pd.DataFrame()

        df = pd.concat(
            self.features,
            ignore_index=True
        )

        df = (
    df.groupby("employee_id")
    .agg(
        file_access_count=("file_access_count", "sum"),
        unique_files=("unique_files", "sum"),
        after_hours_file_access=("after_hours_file_access", "sum"),
        weekend_file_access=("weekend_file_access", "sum"),

        # NEW
        latest_file_timestamp=("latest_file_timestamp", "max")
    )
    .reset_index()
)

        return df