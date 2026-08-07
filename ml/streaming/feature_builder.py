import pandas as pd

# -------------------------------------------------------
# Feature Builder
# -------------------------------------------------------

FEATURE_COLUMNS = [
    "device_connections",
    "emails_sent",
    "files_accessed",
    "websites_visited",
    "logon_count",
    "O",
    "C",
    "E",
    "A",
    "N"
]


def build_features(row: pd.Series) -> pd.DataFrame:
    """
    Convert one incoming log row into the feature format
    expected by the trained Isolation Forest model.
    """

    feature_dict = {}

    for col in FEATURE_COLUMNS:
        feature_dict[col] = row[col]

    return pd.DataFrame([feature_dict])