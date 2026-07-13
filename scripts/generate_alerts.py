"""Generate the SOC alert queue. Spec Milestone 3, Module 9.

    python -m scripts.generate_alerts

Scores every employee for every day, and writes an alert wherever the risk score
earns one. This is the nightly batch job - the thing that fills the queue an analyst
opens in the morning.

SAFE TO RE-RUN. That is not a nice-to-have.
--------------------------------------------
Batch jobs get re-run: after a retrain, after a bug fix, after somebody fat-fingers a
date range. This one UPSERTS on (user_id, alert_date), refreshing the SCORE and
leaving every trace of human work - assignment, notes, verdict - exactly where it
was.

The obvious alternative, DELETE-then-INSERT, is a catastrophe dressed as simplicity:
it silently destroys every verdict an analyst ever recorded. Those verdicts are the
ONLY ground truth that exists in production - CERT ships an answer key, reality does
not - and they are the training signal for the next model. Throwing them away to save
a line of SQL would be the most expensive shortcut in the codebase.
"""

from __future__ import annotations

import logging
import sys
import time

import pandas as pd

from backend.app.alerts import build_alert_rows, persist_alerts, summarise
from backend.app.database import SessionLocal
from backend.app.detection import (
    BASELINE_TRAINING_DAYS,
    add_deviation_features,
    add_temporal_features,
    build_model_matrix,
    load_feature_frame,
)
from backend.app.schema import schema_is_current
from backend.app.scoring import align_features, explain, load_models

logging.basicConfig(level=logging.WARNING, format="%(message)s")


def main() -> int:
    ok, msg = schema_is_current()
    if not ok:
        print(f"ERROR: {msg}")
        return 1

    try:
        xgb, _iso, meta = load_models()
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        return 1

    t0 = time.time()
    print("Generating alerts...")
    print()

    with SessionLocal() as db:
        df = load_feature_frame(db)
        if df.empty:
            print("ERROR: no features. Run: python -m scripts.build_features")
            return 1

        df = add_temporal_features(df)
        cutoff = pd.Timestamp(df["date"].min()) + pd.Timedelta(
            days=BASELINE_TRAINING_DAYS
        )
        df = add_deviation_features(df, training_cutoff=cutoff)

        X, _y, cols = build_model_matrix(df)
        X = align_features(df, meta["feature_columns"])
        prob = xgb.predict_proba(X)[:, 1]

        print(f"  scored {len(df):,} user-days")

        # SHAP for the rows that will actually become alerts.
        #
        # Not for all 330,452 - that would take minutes and 330,000 of the
        # explanations would be for days nobody will ever look at. Explanations are
        # for alerts; alerts are the tiny minority; compute accordingly.
        rows_preview = build_alert_rows(df, prob, explanations=None)
        alert_keys = {(r["user_id"], r["alert_date"]) for r in rows_preview}

        mask = [
            (u, d) in alert_keys
            for u, d in zip(
                df["user_id"].to_numpy(),
                pd.to_datetime(df["date"]).dt.date.to_numpy(),
                strict=True,
            )
        ]
        sub = df[mask]
        print(f"  explaining {len(sub):,} alert-worthy days with SHAP...")

        exps = explain(
            xgb,
            align_features(sub, meta["feature_columns"]),
            meta["feature_columns"],
            sub["user_id"].tolist(),
            pd.to_datetime(sub["date"]).dt.date.tolist(),
            prob[mask],
        )

        rows = build_alert_rows(df, prob, explanations=exps)
        persist_alerts(db, rows)
        s = summarise(db)

    print()
    print("=" * 70)
    print("THE ALERT QUEUE")
    print("=" * 70)
    print()
    print(f"  {'severity':<16} {'count':>8}")
    print("  " + "-" * 26)
    for sev in ("critical", "high", "medium", "low", "informational"):
        print(f"  {sev:<16} {s['by_severity'].get(sev, 0):>8,}")
    print("  " + "-" * 26)
    print(f"  {'TOTAL':<16} {s['total']:>8,}")
    print()
    print(f"  {'status':<26} {'count':>8}")
    print("  " + "-" * 36)
    for st, n in sorted(s["by_status"].items()):
        print(f"  {st:<26} {n:>8,}")
    print()
    print(f"Completed in {time.time() - t0:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())