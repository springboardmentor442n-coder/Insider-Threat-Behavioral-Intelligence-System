"""
preprocess.py
-----------------
Loads and cleans the CERT r4.2 insider threat dataset (logon, device, email,
file, http logs). This is step 1 of the ml pipeline.

Usage (in a notebook or script):
    from ml.preprocess import load_and_clean_all

    cleaned = load_and_clean_all(
        base_path="/kaggle/working/r4.2/r4.2/",
        out_path="/kaggle/working/cleaned/"
    )
    logon = cleaned["logon"]
    device = cleaned["device"]
    ...
"""

import os
import pandas as pd

FILES = ["logon", "device", "email", "file", "http"]


def _clean_single(df: pd.DataFrame, name: str, verbose: bool = True) -> pd.DataFrame:
    """Clean one raw CERT log dataframe."""
    if verbose:
        print(f"\n--- Cleaning {name} ---")
        print("Raw shape:", df.shape)

    # Parse dates
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        before = len(df)
        df = df.dropna(subset=["date"])
        if verbose:
            print(f"Dropped {before - len(df)} rows with unparseable dates")

    # Drop exact duplicates
    before = len(df)
    df = df.drop_duplicates()
    if verbose:
        print(f"Dropped {before - len(df)} duplicate rows")

    # Drop rows missing critical identifiers
    required = [c for c in ["user", "pc"] if c in df.columns]
    if required:
        before = len(df)
        df = df.dropna(subset=required)
        if verbose:
            print(f"Dropped {before - len(df)} rows missing {required}")

    # Strip whitespace from text columns
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip()

    # Sort chronologically
    if "date" in df.columns:
        df = df.sort_values("date").reset_index(drop=True)

    if verbose:
        print("Clean shape:", df.shape)

    return df


def load_and_clean_all(base_path: str, out_path: str = None, verbose: bool = True) -> dict:
    """
    Load all 5 CERT log files from base_path, clean each one, optionally
    save cleaned copies to out_path, and return them as a dict of DataFrames.
    """
    if out_path:
        os.makedirs(out_path, exist_ok=True)

    cleaned = {}
    for name in FILES:
        path = os.path.join(base_path, f"{name}.csv")
        df = pd.read_csv(path)
        df = _clean_single(df, name, verbose=verbose)
        cleaned[name] = df

        if out_path:
            out_file = os.path.join(out_path, f"{name}_clean.csv")
            df.to_csv(out_file, index=False)
            if verbose:
                print(f"Saved -> {out_file}")

    if verbose:
        print("\n=== Summary ===")
        for name, df in cleaned.items():
            n_users = df["user"].nunique() if "user" in df.columns else "N/A"
            if "date" in df.columns and len(df) > 0:
                date_range = f"{df['date'].min()} to {df['date'].max()}"
            else:
                date_range = "N/A"
            print(f"{name}: {len(df)} rows, {n_users} unique users, dates: {date_range}")

    return cleaned


if __name__ == "__main__":
    # Adjust these paths to match your Kaggle environment
    BASE_PATH = "/kaggle/working/r4.2/r4.2/"
    OUT_PATH = "/kaggle/working/cleaned/"
    cleaned = load_and_clean_all(BASE_PATH, OUT_PATH)
