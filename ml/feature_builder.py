import pandas as pd



class FeatureBuilder:

    def __init__(self):
        self.features = None

    def load_login_features(self, login_df):
        self.features = login_df.copy()

    def merge_http_features(self, http_df):

        self.features = self.features.merge(
            http_df,
            on="employee_id",
            how="left"
        )

    def merge_email_features(self, email_df):

        self.features = self.features.merge(
            email_df,
            on="employee_id",
            how="left"
        )

    def merge_file_features(self, file_df):

        self.features = self.features.merge(
            file_df,
            on="employee_id",
            how="left"
        )

    def merge_device_features(self, device_df):

        self.features = self.features.merge(
            device_df,
            on="employee_id",
            how="left"
        )

    def finalize(self):

        timestamp_columns = [
            "latest_login_timestamp",
            "latest_http_timestamp",
            "latest_email_timestamp",
            "latest_file_timestamp",
            "latest_device_timestamp",
        ]

        # Fill missing timestamps with NaT (not 0)
        for col in timestamp_columns:
            if col in self.features.columns:
                self.features[col] = pd.to_datetime(
                    self.features[col],
                    errors="coerce"
                )

        # Latest event across all activities
        self.features["event_timestamp"] = (
            self.features[timestamp_columns]
            .max(axis=1)
        )

        # Fill only numeric columns with 0
        numeric_columns = self.features.select_dtypes(
            include=["number"]
        ).columns

        self.features[numeric_columns] = (
            self.features[numeric_columns]
            .fillna(0)
        )

        return self.features
    