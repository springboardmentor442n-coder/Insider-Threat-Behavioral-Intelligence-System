"""CLI entry point for loading the CERT r4.2 dataset into PostgreSQL.

    python -m scripts.ingest_cert                 # everything, including http.csv
    python -m scripts.ingest_cert --skip-http     # fast: skips the 13.9 GB file

Run this ONCE. It clears and reloads every ingested table, so it is safe to
re-run, but there is no reason to unless the data changed.

Expect the full run to take a while. http.csv alone is 13.9 GB of CSV, and no
amount of cleverness makes reading 13.9 GB instant. --skip-http gets you a
working database in a couple of minutes so you can build the rest of the
pipeline, at the cost of the scenario-1 and scenario-2 web signals.
"""

import argparse
import sys
from pathlib import Path

from backend.app.config import get_settings
from backend.app.database import Base, SessionLocal, engine
from backend.app.schema import upgrade_to_head
from backend.app.ingestion import (
    get_counts,
    ingest_http_summary,
    recreate_derived_tables,
    run_ingestion,
)

# These imports look unused, and they are not. Importing a models module has the
# SIDE EFFECT of registering its ORM classes on Base.metadata. Without them,
# create_all() runs against a half-empty registry and silently creates only some
# of the tables - and then clear_all(), which deletes from ALL of them, crashes
# with "relation daily_features does not exist" on a fresh database.
#
# Found by running the full pipeline against a database with no tables at all,
# which is exactly the state a new machine is in. Unit tests did not catch it
# because they run after the tables already exist.
from backend.app import features_models, models  # noqa: F401


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingest the CERT r4.2 dataset.")
    parser.add_argument(
        "--skip-http",
        action="store_true",
        help="Skip http.csv (13.9 GB). Much faster; loses the web-activity signals.",
    )
    parser.add_argument(
        "--http-only",
        action="store_true",
        help=(
            "Re-stream ONLY http.csv, leaving the other tables alone. Use this "
            "when the http schema changed but logon/device/file/email are "
            "already loaded correctly - it saves redoing 4 minutes of work that "
            "was already right."
        ),
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=None,
        help="Path to the data directory (defaults to CERT_DATA_DIR from .env).",
    )
    args = parser.parse_args()

    settings = get_settings()
    data_dir = args.data_dir or Path(settings.CERT_DATA_DIR)

    if not data_dir.is_dir():
        print(f"ERROR: data directory not found: {data_dir.resolve()}")
        return 1

    # Fail early and clearly if the dataset is not where we think it is, rather
    # than 40 minutes into a load.
    required = [
        data_dir / "r4.2" / "logon.csv",
        data_dir / "r4.2" / "device.csv",
        data_dir / "r4.2" / "file.csv",
        data_dir / "r4.2" / "email.csv",
        data_dir / "r4.2" / "LDAP",
        data_dir / "answers" / "insiders.csv",
    ]
    missing = [p for p in required if not p.exists()]
    if missing:
        print("ERROR: required dataset files are missing:")
        for p in missing:
            print(f"  - {p}")
        return 1

    print(f"Data directory : {data_dir.resolve()}")
    print(f"Include http   : {not args.skip_http}")
    if not args.skip_http:
        print("  (http.csv is 13.9 GB - this will take a while)")
    print()

    # Bring the database up to the schema the code expects.
    #
    # This used to be create_all(), which creates missing tables and silently
    # ignores existing ones that are out of date. That is how a new column produced
    # a clean run followed by a crash on the first INSERT - twice, once after seven
    # minutes of streaming 13.9 GB of http.csv.
    #
    # `alembic upgrade head` ALTERs in place. It is idempotent: on an already-current
    # database it does nothing and costs milliseconds.
    upgrade_to_head()

    # --- http-only path ----------------------------------------------------
    # The derived tables get DROPPED and rebuilt, because create_all() will not
    # add a column to a table that already exists - which is precisely the bug
    # that wasted a full 13.9 GB stream and then died on the final INSERT.
    if args.http_only:
        print("Re-streaming http.csv only.")
        print("Dropping and recreating the derived tables (schema may have changed).")
        recreate_derived_tables(engine)

        db = SessionLocal()
        try:
            from sqlalchemy import select

            from backend.app.models import Employee

            known = {uid for (uid,) in db.execute(select(Employee.user_id)).all()}
            if not known:
                print()
                print("ERROR: no employees in the database.")
                print("       --http-only assumes a previous full ingestion loaded them.")
                print("       Run without --http-only to do a full load.")
                return 1

            print(f"Found {len(known):,} employees already loaded.")
            print()
            rows = ingest_http_summary(db, data_dir, known)
            print()
            print(f"http_daily_summary rebuilt: {rows:,} rows")
            print()
            print("Now run:  python -m scripts.build_features")
            return 0
        finally:
            db.close()

    db = SessionLocal()
    try:
        print("Ingesting...")
        stats = run_ingestion(db, data_dir, include_http=not args.skip_http)

        print()
        print("Done in", f"{stats.duration_seconds}s")
        print()
        print("Row counts:")
        for table, count in get_counts(db).items():
            print(f"  {table:<20} {count:>12,}")

        print()
        counts = get_counts(db)
        # Sanity checks against the published r4.2 figures. If these are wrong,
        # something went wrong, and every downstream metric is untrustworthy.
        if counts.get("malicious_event_days", 0) == 0:
            print("  WARNING: no malicious EVENT-DAY labels were ingested.")
            print("           The answers/r4.2-1, -2, -3 folders were not found.")
            print("           train_detect will report only ONE labelling convention.")
        if counts["employees"] != 1000:
            print(f"  WARNING: expected 1000 employees, got {counts['employees']}")
        if counts["insiders"] != 70:
            print(f"  WARNING: expected 70 insiders, got {counts['insiders']}")
        if counts["employees"] == 1000 and counts["insiders"] == 70:
            print("  Sanity check PASSED: 1000 employees, 70 insiders (matches r4.2).")

        return 0
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())