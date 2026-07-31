import pandas as pd
from collections import defaultdict
from datetime import time


CHUNK_SIZE = 100000


def extract_http_features(file_path):
    """
    Extract HTTP behavioral features from CERT http.csv
    Returns a dictionary:
    {
        employee_id: {
            feature_name: value
        }
    }
    """

    employee_features = defaultdict(lambda: {
        "http_visit_count": 0,
        "unique_websites": set(),
        "after_hours_http": 0,
        "weekend_http": 0,
        "unique_http_pcs": set()
    })

    for chunk in pd.read_csv(
            file_path,
            chunksize=CHUNK_SIZE,
            parse_dates=["date"]):

        for _, row in chunk.iterrows():

            employee = row["user"]

            employee_features[employee]["http_visit_count"] += 1

            employee_features[employee]["unique_websites"].add(row["url"])

            employee_features[employee]["unique_http_pcs"].add(row["pc"])

            hour = row["date"].hour

            if hour < 8 or hour >= 18:
                employee_features[employee]["after_hours_http"] += 1

            if row["date"].weekday() >= 5:
                employee_features[employee]["weekend_http"] += 1

    final_features = {}

    for employee, feature in employee_features.items():

        final_features[employee] = {
            "http_visit_count": feature["http_visit_count"],
            "unique_websites": len(feature["unique_websites"]),
            "after_hours_http": feature["after_hours_http"],
            "weekend_http": feature["weekend_http"],
            "unique_http_pcs": len(feature["unique_http_pcs"])
        }

    return final_features