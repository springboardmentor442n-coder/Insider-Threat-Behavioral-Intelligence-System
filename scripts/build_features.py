"""Build behavioural features and per-user baselines from the ingested data.

    python -m scripts.build_features

Run this AFTER scripts.ingest_cert. It reads the raw event tables and produces:

  daily_features  - one row per user per active day (~330k rows)
  user_baselines  - one row per user: what "normal" looks like for them

Then it prints a validation table comparing the insiders' malicious days against
everyone else's normal days. That table is the honest test of whether the feature
engineering worked: if the malicious days do not look different in the RAW
AVERAGES, before any model has been trained, then the features carry no signal
and nothing downstream can rescue them.
"""

import sys

from backend.app.database import Base, SessionLocal, engine
from backend.app.features import (
    check_baseline_contamination,
    get_feature_counts,
    recreate_feature_tables,
    run_feature_engineering,
    validate_features,
)

# Importing the models registers them on Base.metadata so create_all() sees them.
from backend.app import features_models, models  # noqa: F401


def _row(label: str, d: dict, keys: list[str]) -> str:
    cells = "".join(f"{str(d.get(k, '')):>15}" for k in keys)
    return f"{label:<14}{cells}"


def main() -> int:
    # ALWAYS drop and rebuild daily_features + user_baselines.
    #
    # Not create_all() - create_all() does NOT alter tables that already exist, so
    # any new column on DailyFeatures silently fails to appear and the build dies
    # on the INSERT with "column ... does not exist". That has now happened twice.
    #
    # These tables are fully DERIVED: every row is recomputed from the raw events
    # on every run. Dropping them costs nothing and makes schema drift impossible
    # rather than merely unlikely.
    #
    # http_daily_summary is NOT touched - it is built during ingestion by streaming
    # 13.9 GB of http.csv, and dropping it would silently force a full re-ingest.
    recreate_feature_tables(engine)
    db = SessionLocal()

    try:
        print("Building daily features and baselines...")
        print("(aggregating 4.3M events in Postgres - this takes a minute)")
        print()

        result = run_feature_engineering(db)

        print(f"Done in {result['duration_seconds']}s")
        print()
        counts = get_feature_counts(db)
        for k, v in counts.items():
            print(f"  {k:<22} {v:>10,}")

        if counts["daily_feature_rows"] == 0:
            print()
            print("ERROR: no features were built. Did you run scripts.ingest_cert?")
            return 1

        # --- Baseline hygiene --------------------------------------------------
        # A baseline built from days that include the attack is worse than no
        # baseline at all: the insider's own spike inflates his own "normal", and
        # he looks LESS anomalous the worse he behaves. We exclude malicious days
        # from the baseline - but we say so, loudly, rather than hiding it.
        print()
        print("-" * 72)
        c = check_baseline_contamination(db)
        print(f"Baseline training window : {c['data_starts']} -> {c['baseline_cutoff']}")
        print(f"First attack day in data : {c['first_attack_day']}")
        if c["contaminated"]:
            print(
                f"  NOTE: {c['window_attack_days']:,} of {c['window_days']:,} days in "
                "the window are malicious."
            )
            print("  They were EXCLUDED from the baseline (contamination guard active).")
            print("  Baselines are built only from behaviour known to be benign.")
        else:
            print("  Window is clean: no attack days fall inside it.")
        print("-" * 72)

        print()
        print("=" * 104)
        print("VALIDATION - do the insiders' malicious days actually look different?")
        print("=" * 104)

        v = validate_features(db)
        keys = [
            "after_hours", "usb", "files", "job_sites",
            "wikileaks", "hacking_sites", "exe_files", "pct_boss_pc",
        ]

        header = "".join(f"{k:>15}" for k in keys)
        print(f"{'':<14}{header}")
        print("-" * 104)
        print(_row("MALICIOUS", v["malicious"], keys))
        print(_row("normal", v["normal"], keys))
        print("-" * 104)

        m, n = v["malicious"], v["normal"]
        print(f"  malicious days: {m['days']:,}   normal days: {n['days']:,}")
        print()

        # Ratios - the honest measure of how much signal each feature carries.
        print("Signal strength (malicious average / normal average):")
        for k in keys:
            mv, nv = float(m.get(k) or 0), float(n.get(k) or 0)
            if nv > 0:
                print(f"  {k:<18} {mv / nv:>8.1f}x")
            elif mv > 0:
                print(f"  {k:<18} {'infinite':>8}   (normal users NEVER do this)")

        print()
        print("=" * 104)
        print("BY SCENARIO - each attack should light up its own features")
        print("=" * 104)
        skeys = ["malicious_days", "after_hours", "usb", "job_sites",
                 "wikileaks", "hacking_sites"]
        print(f"{'scenario':<12}" + "".join(f"{k:>16}" for k in skeys))
        print("-" * 104)
        for row in v["by_scenario"]:
            cells = "".join(f"{str(row.get(k, '')):>16}" for k in skeys)
            print(f"{row['scenario']:<12}{cells}")

        print()
        print("Expected, per answers/scenarios.txt:")
        print("  scenario 1 -> after-hours + USB + wikileaks")
        print("  scenario 2 -> job_sites, then a USB spike")
        print("  scenario 3 -> hacking_sites (keylogger) + supervisor's PC")

        return 0
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())