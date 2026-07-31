import pandas as pd


class HTTPFeatureExtractor:

    def __init__(self):
        self.features = None

    def process_chunk(self, chunk: pd.DataFrame):

        chunk["date"] = pd.to_datetime(
            chunk["date"],
            errors="coerce"
        )

        chunk["hour"] = chunk["date"].dt.hour

        chunk["is_weekend"] = (
            chunk["date"].dt.dayofweek >= 5
        )

        chunk["after_hours"] = (
            (chunk["hour"] < 8) |
            (chunk["hour"] > 18)
        )

        grouped = (
    chunk.groupby("user")
    .agg(
        http_visit_count=("url", "count"),
        unique_websites=("url", "nunique"),
        after_hours_http=("after_hours", "sum"),
        weekend_http=("is_weekend", "sum"),
        unique_http_pcs=("pc", "nunique"),
        latest_http_timestamp=("date", "max")
    )
    .reset_index()
    .rename(
        columns={"user": "employee_id"}
    )
)

        if self.features is None:

            self.features = grouped

        else:

            self.features = pd.concat(
                [self.features, grouped],
                ignore_index=True
            )

    def finalize(self):

        if self.features is None:
            return pd.DataFrame()

        return (
    self.features
    .groupby("employee_id")
    .agg(
        http_visit_count=("http_visit_count", "sum"),
        unique_websites=("unique_websites", "max"),
        after_hours_http=("after_hours_http", "sum"),
        weekend_http=("weekend_http", "sum"),
        unique_http_pcs=("unique_http_pcs", "max"),

        # NEW
        latest_http_timestamp=("latest_http_timestamp", "max")
    )
    .reset_index()
)