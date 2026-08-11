from pathlib import Path

import pandas as pd

LDAP_FOLDER = (
    Path(__file__)
    .resolve()
    .parents[2]
    / "datasets"
    / "raw"
    / "r4.2"
    / "LDAP"
)

_cached_directory = None


def load_employee_directory():
    """
    Loads every monthly LDAP file and creates one employee directory.

    Cached after first load.
    """

    global _cached_directory

    if _cached_directory is not None:
        return _cached_directory

    csv_files = sorted(LDAP_FOLDER.glob("*.csv"))

    frames = []

    for file in csv_files:
        try:
            df = pd.read_csv(file)
            frames.append(df)
        except Exception:
            continue

    if not frames:
        _cached_directory = pd.DataFrame()
        return _cached_directory

    directory = pd.concat(
        frames,
        ignore_index=True,
    )

# Standardize the key column
    directory = directory.rename(
        columns={
            "user_id": "user"
        }
    )

    directory = directory.drop_duplicates(
        subset="user",
        keep="last",
    )

    _cached_directory = directory

    return _cached_directory

