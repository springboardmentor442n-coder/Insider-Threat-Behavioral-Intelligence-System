import pandas as pd


def load_dataset(file_path):
    """
    Load the CERT Insider Threat dataset.
    """
    return pd.read_csv(file_path)


def preprocess_logon_data(df):
    """
    Perform preprocessing and feature engineering.
    """

    # Convert date column
    df["date"] = pd.to_datetime(df["date"])

    # Feature Engineering
    df["login_hour"] = df["date"].dt.hour
    df["day"] = df["date"].dt.day
    df["month"] = df["date"].dt.month
    df["weekday"] = df["date"].dt.day_name()

    # Binary feature
    df["is_after_hours"] = df["login_hour"].apply(
        lambda x: 1 if x < 8 or x > 18 else 0
    )

    return df


if __name__ == "__main__":

    print("Insider Threat Behavioral Intelligence System")
    print("Preprocessing Module Ready")