import pandas as pd


class EmailFeatureExtractor:

    def __init__(self):
        self.features = []

    def process_chunk(self, chunk):

        chunk["date"] = pd.to_datetime(
            chunk["date"],
            errors="coerce"
        )

        chunk["hour"] = chunk["date"].dt.hour

        chunk["employee_id"] = chunk["user"]

        # External email detection
        chunk["is_external"] = (
            ~chunk["to"].str.endswith(
                "@dtaa.com",
                na=False
            )
        ).astype(int)

        grouped = (
            chunk.groupby("employee_id")
            .agg(
                email_sent=("employee_id", "size"),
                external_emails=("is_external", "sum"),
                after_hours_emails=(
                    "hour",
                    lambda x: ((x < 8) | (x > 18)).sum()
                ),
                latest_email_timestamp=("date", "max")
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
        email_sent=("email_sent", "sum"),
        external_emails=("external_emails", "sum"),
        after_hours_emails=("after_hours_emails", "sum"),
        latest_email_timestamp=("latest_email_timestamp", "max")
    )
    .reset_index()
)

        return df
    