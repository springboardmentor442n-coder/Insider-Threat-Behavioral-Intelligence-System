import os
import pandas as pd

CHUNK_SIZE = 200_000
BASE_PATH = "/kaggle/input/datasets/andrihjonior/cert-insider-threat-dataset-r4-2/r4.2/"
OUT_PATH = "/kaggle/working/cleaned/"

os.makedirs(OUT_PATH, exist_ok=True)


def clean_file_chunked(name, verbose=True):
    """Clean one CERT log file using chunked reading (memory-safe)."""
    path = os.path.join(BASE_PATH, f"{name}.csv")
    out_file = os.path.join(OUT_PATH, f"{name}_clean.csv")

    first_chunk = True
    total_rows = 0
    users = set()

    for i, chunk in enumerate(pd.read_csv(path, chunksize=CHUNK_SIZE)):
        if "date" in chunk.columns:
            chunk["date"] = pd.to_datetime(chunk["date"], errors="coerce")
            chunk = chunk.dropna(subset=["date"])

        chunk = chunk.drop_duplicates()

        required = [c for c in ["user", "pc"] if c in chunk.columns]
        if required:
            chunk = chunk.dropna(subset=required)

        for col in chunk.select_dtypes(include="object").columns:
            chunk[col] = chunk[col].astype(str).str.strip()

        chunk.to_csv(out_file, mode="w" if first_chunk else "a", header=first_chunk, index=False)
        first_chunk = False

        total_rows += len(chunk)
        if "user" in chunk.columns:
            users.update(chunk["user"].unique())

        if verbose:
            print(f"{name}: processed chunk {i+1}, {len(chunk)} rows")

    if verbose:
        print(f"\nDone. {name}: {total_rows} rows, {len(users)} unique users\n")

    return total_rows, len(users)


def load_and_clean_all(verbose=True):
    """Clean all 5 CERT log files, one at a time, chunked."""
    summary = {}
    for name in ["logon", "device", "email", "file", "http"]:
        rows, users = clean_file_chunked(name, verbose=verbose)
        summary[name] = {"rows": rows, "users": users}
    return summary


if __name__ == "__main__":
    summary = load_and_clean_all()
    print("=== Summary ===")
    for name, stats in summary.items():
        print(f"{name}: {stats['rows']} rows, {stats['users']} unique users")
