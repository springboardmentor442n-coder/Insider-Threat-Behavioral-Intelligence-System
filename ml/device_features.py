import pandas as pd


class DeviceFeatureExtractor:

    def __init__(self):
        self.features = []

    def process_chunk(self, chunk):

        chunk["date"] = pd.to_datetime(
            chunk["date"],
            errors="coerce"
        )

        chunk["hour"] = chunk["date"].dt.hour

        chunk["employee_id"] = chunk["user"]

        chunk["is_connect"] = (
            chunk["activity"] == "Connect"
        ).astype(int)

        chunk["is_disconnect"] = (
            chunk["activity"] == "Disconnect"
        ).astype(int)

        chunk["is_weekend"] = (
            chunk["date"].dt.dayofweek >= 5
        ).astype(int)

        grouped = (
            chunk.groupby("employee_id")
            .agg(
                device_usage_count=("employee_id", "size"),
                connect_count=("is_connect", "sum"),
                disconnect_count=("is_disconnect", "sum"),
                after_hours_device_usage=(
                    "hour",
                    lambda x: ((x < 8) | (x > 18)).sum()
                ),
                weekend_device_usage=("is_weekend", "sum"),
                latest_device_timestamp=("date", "max")
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
        device_usage_count=("device_usage_count", "sum"),
        connect_count=("connect_count", "sum"),
        disconnect_count=("disconnect_count", "sum"),
        after_hours_device_usage=("after_hours_device_usage", "sum"),
        weekend_device_usage=("weekend_device_usage", "sum"),

        # NEW
        latest_device_timestamp=("latest_device_timestamp", "max")
    )
    .reset_index()
)

        return df