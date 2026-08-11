"""
Utility functions for loading CSV datasets.
"""

import pandas as pd


def load_csv(path):
    """
    Load the complete CSV.
    Used by ML scripts and full dataset processing.
    """

    try:
        df = pd.read_csv(path)
        df = df.astype(object).where(pd.notnull(df), None)
        return df

    except Exception as e:
        print(f"Error loading {path}")
        print(e)
        return pd.DataFrame()


def load_csv_preview(path, rows=100):
    """
    Load only the first N rows.
    Used by FastAPI endpoints for quick preview.
    """

    try:
        df = pd.read_csv(
            path,
            nrows=rows,
        )

        df = df.astype(object).where(pd.notnull(df), None)

        return df

    except Exception as e:
        print(f"Error loading {path}")
        print(e)
        return pd.DataFrame()
