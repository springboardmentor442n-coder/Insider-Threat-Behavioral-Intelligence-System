#!/usr/bin/env python
"""Run the CERT ingestion pipeline and write data/daily_user_features.csv."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import Config  # noqa: E402
from app.ml.features import build_daily_features  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--raw", default=None, help="raw CERT r4.2 directory")
    ap.add_argument("--out", default=None, help="output CSV path")
    args = ap.parse_args()

    Config.ensure_dirs()
    raw = Path(args.raw) if args.raw else Config.RAW_DIR
    out = Path(args.out) if args.out else Config.FEATURES_CSV

    print(f"Building daily user features from {raw}")
    df = build_daily_features(raw)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(
        f"Wrote {out} — {len(df):,} user-days, {df['user'].nunique():,} users, "
        f"{int(df['is_insider'].sum()):,} labelled malicious"
    )


if __name__ == "__main__":
    main()
