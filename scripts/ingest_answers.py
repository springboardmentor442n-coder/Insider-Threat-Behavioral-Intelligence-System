"""Ingest ONLY the answer key. Seconds, not a 15-minute re-import.

    python -m scripts.ingest_answers

WHY THIS EXISTS
---------------
The event-day labels live in three small folders - answers/r4.2-1/, -2/, -3/ - about
966 rows in total. Reading them takes under two seconds.

To pick them up, I told you to re-run `ingest_cert`. Which WIPES THE DATABASE and
re-imports 32.7 million events, including streaming 13.9 GB of http.csv, and takes
fifteen minutes. To read 966 rows.

That was a bad instruction. Ingestion is all-or-nothing because that is how it was
first written, and I never questioned it when I bolted a new answer source onto the
side. A pipeline that can only be run in full is a pipeline nobody runs.

This script does the one thing that actually needs doing. It touches nothing else:
not the events, not the employees, not the features, not the alerts.

AFTER RUNNING THIS
------------------
    python -m scripts.build_features     (~45s - it must pick up the new label)
    python -m scripts.train_detect

build_features IS required. The label lives on daily_features, and that table is
rebuilt from the event tables - it does not know about malicious_event_days until it
is rebuilt against it.
"""

from __future__ import annotations

import logging
import sys
import time
from pathlib import Path

from sqlalchemy import func, select

from backend.app.config import get_settings
from backend.app.database import SessionLocal
from backend.app.ingestion import ingest_malicious_event_days
from backend.app.models import MaliciousEventDay
from backend.app.schema import schema_is_current

logging.basicConfig(level=logging.INFO, format="  %(message)s")


def main() -> int:
    ok, message = schema_is_current()
    if not ok:
        print(f"ERROR: {message}")
        print("\n    alembic upgrade head")
        return 1

    settings = get_settings()
    data_dir = Path(settings.CERT_DATA_DIR)

    answers = data_dir / "answers"
    if not answers.exists():
        print(f"ERROR: no answers/ directory at {answers}")
        return 1

    missing = [f"r4.2-{s}" for s in (1, 2, 3) if not (answers / f"r4.2-{s}").exists()]
    if missing:
        print(f"ERROR: missing answer folders: {missing}")
        print(f"       expected under {answers}")
        return 1

    t0 = time.perf_counter()
    print("Reading the per-insider answer files...")
    print()

    with SessionLocal() as db:
        n = ingest_malicious_event_days(db, data_dir)

        # The two conventions, side by side, straight from the database.
        event_days = db.scalar(select(func.count()).select_from(MaliciousEventDay))
        event_users = db.scalar(
            select(func.count(func.distinct(MaliciousEventDay.user_id)))
        )

        # The window count must come from daily_features, NOT from date arithmetic
        # on insiders.csv.
        #
        # A calendar window of 40 days is not 40 malicious ROWS: daily_features only
        # has a row for a day on which the employee actually did something. Weekends,
        # holidays and leave produce no row at all. Counting calendar days gives an
        # upper bound that does not correspond to anything in the table, and the two
        # numbers are then not comparable - which is the exact sin this whole exercise
        # exists to correct.
        from backend.app.features_models import DailyFeatures

        window_days = db.scalar(
            select(func.count()).select_from(DailyFeatures)
            .where(DailyFeatures.is_malicious)
        ) or 0

        per_scenario = db.execute(
            select(
                MaliciousEventDay.scenario,
                func.count(func.distinct(MaliciousEventDay.user_id)),
                func.count(),
            ).group_by(MaliciousEventDay.scenario)
        ).all()

    print()
    print("=" * 70)
    print("THE TWO LABELLING CONVENTIONS")
    print("=" * 70)
    print()
    if window_days:
        print(f"  WINDOW    (insiders.csv start -> end)   {window_days:>7,} user-days")
        print(f"  EVENT-DAY (attacks that actually ran)   {event_days:>7,} user-days")
        print()
        padding = window_days - event_days
        if padding > 0:
            print(f"  {padding:,} of the window days "
                  f"({100 * padding / window_days:.0f}%) contain NO malicious activity.")
        else:
            print("  NOTE: more event-days than window-days. That should be impossible")
            print("  - every malicious event ought to fall inside its own insider's")
            print("  window. Either the answer files and insiders.csv disagree, or one")
            print("  of them is being read wrong. Worth knowing before quoting a number.")
    else:
        print(f"  EVENT-DAY (attacks that actually ran)   {event_days:>7,} user-days")
        print()
        print("  daily_features is empty, so there is nothing to compare against yet.")
        print("  Run build_features and the comparison will appear in train_detect.")
    print()
    print(f"  {'scenario':<10} {'insiders':>9} {'event days':>12}")
    print("  " + "-" * 33)
    for scen, users, days in sorted(per_scenario):
        print(f"  {scen:<10} {users:>9} {days:>12,}")
    print()
    print(f"  ({event_users} insiders have event-day labels)")
    print()
    print("=" * 70)
    print(f"Done in {time.perf_counter() - t0:.1f}s. {n:,} rows.")
    print()
    print("  NOW RUN:  python -m scripts.build_features")
    print()
    print("  The label lives on daily_features, and that table is rebuilt from the")
    print("  event tables - it does not know about any of this until it is rebuilt.")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())