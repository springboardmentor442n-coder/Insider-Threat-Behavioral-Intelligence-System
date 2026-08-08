#!/usr/bin/env python
"""One-command setup: generate data (if needed) -> engineer features -> train.

    python scripts/bootstrap.py                 # full setup, synthetic corpus
    python scripts/bootstrap.py --raw /path/r4.2  # use the real CERT dataset
    python scripts/bootstrap.py --force         # regenerate everything
"""

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config import Config  # noqa: E402


def step(n, total, title):
    print(f"\n[{n}/{total}] {title}\n{'-' * 60}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--raw", default=None, help="existing CERT r4.2 directory")
    ap.add_argument("--users", type=int, default=160)
    ap.add_argument("--days", type=int, default=160)
    ap.add_argument("--insider-rate", type=float, default=0.07)
    ap.add_argument("--backend", choices=["auto", "gb", "xgboost"], default="auto")
    ap.add_argument("--force", action="store_true", help="rebuild even if artefacts exist")
    args = ap.parse_args()

    Config.ensure_dirs()
    raw_dir = Path(args.raw) if args.raw else Config.RAW_DIR
    total = 3

    step(1, total, "Raw activity logs")
    have_raw = all((raw_dir / f).exists() for f in
                   ["logon.csv", "device.csv", "file.csv", "email.csv", "http.csv"])
    if have_raw and not args.force:
        print(f"  Found existing raw logs in {raw_dir} — skipping generation")
    elif args.raw:
        raise SystemExit(f"--raw was given but {raw_dir} is missing CERT log files")
    else:
        subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "generate_data.py"),
             "--users", str(args.users), "--days", str(args.days),
             "--insider-rate", str(args.insider_rate)],
            check=True,
        )

    step(2, total, "Feature engineering")
    if Config.FEATURES_CSV.exists() and not args.force:
        print(f"  Found {Config.FEATURES_CSV} — skipping (use --force to rebuild)")
    else:
        cmd = [sys.executable, str(ROOT / "scripts" / "build_features.py")]
        if args.raw:
            cmd += ["--raw", str(raw_dir)]
        subprocess.run(cmd, check=True)

    step(3, total, "Model training")
    from app.ml.train import train  # noqa: PLC0415

    metrics = train(backend=args.backend)

    print("\n" + "=" * 60)
    print("Bootstrap complete.")
    print(f"  Model      : {metrics['model']} ({metrics['n_features']} features)")
    print(f"  PR-AUC     : {metrics['pr_auc']}   ROC-AUC: {metrics['roc_auc']}")
    print(f"  Precision  : {metrics['precision']}   Recall: {metrics['recall']}   "
          f"F1: {metrics['f1']}")
    print(f"  User recall: {metrics['user_level_recall']}")
    print("\nStart the console with:  python run.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
