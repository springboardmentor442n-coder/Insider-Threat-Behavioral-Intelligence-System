"""One-time: bring an EXISTING database under Alembic's control.

WHY YOU NEED THIS, AND WHY `alembic upgrade head` ALONE WILL NOT WORK
---------------------------------------------------------------------
Your database already has every table - they were created by the old
`Base.metadata.create_all()` path, and they are full of real data: 32.7 million
events and 330,452 feature rows that took fifteen minutes to ingest.

Alembic does not know that. Its first migration says "CREATE TABLE employees", so
running `alembic upgrade head` on your database fails immediately with:

    psycopg2.errors.DuplicateTable: relation "employees" already exists

The fix is to STAMP: tell Alembic "the initial migration is already applied - the
tables it would have created are right there". Alembic writes the version number
and moves on to the migrations that actually have work to do.

This script does that, and only if it is safe:

    1. If the database is already under Alembic, it does nothing.
    2. If the database is EMPTY, it just migrates normally.
    3. If the database has tables but no alembic_version, it stamps the initial
       revision and then upgrades - which applies the auth-hardening columns and
       the server defaults, and touches nothing else.

NOTHING IS DROPPED. NOTHING IS RE-INGESTED. That is the entire point of Alembic,
and it is the thing create_all() could never do.
"""

from __future__ import annotations

import sys

from sqlalchemy import inspect, text

from backend.app.database import engine
from backend.app.schema import PROJECT_ROOT

# The first migration - the one that creates the tables you already have.
INITIAL_REVISION = "3c670d1086a0"


def main() -> int:
    insp = inspect(engine)
    tables = [t for t in insp.get_table_names() if t != "alembic_version"]
    has_alembic = insp.has_table("alembic_version")

    print("=" * 74)
    print("ADOPTING ALEMBIC")
    print("=" * 74)
    print()
    print(f"  tables found        : {len(tables)}")
    print(f"  under alembic already: {has_alembic}")
    print()

    from alembic import command
    from alembic.config import Config

    from backend.app.config import get_settings

    cfg = Config(str(PROJECT_ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(PROJECT_ROOT / "migrations"))
    cfg.set_main_option("sqlalchemy.url", get_settings().DATABASE_URL)

    if has_alembic:
        with engine.connect() as c:
            v = c.execute(text("SELECT version_num FROM alembic_version")).scalar()
        print(f"  Already under Alembic (at {v}). Just upgrading.")
        print()
        command.upgrade(cfg, "head")

    elif not tables:
        print("  Empty database. Running every migration from scratch.")
        print()
        command.upgrade(cfg, "head")

    else:
        # THE CASE THAT MATTERS: real tables, real data, no Alembic.
        print("  Your database has tables but no Alembic version.")
        print()
        print(f"  Stamping it at {INITIAL_REVISION} - which tells Alembic the tables")
        print("  it would have created ALREADY EXIST, so it must not try again.")
        print()
        print("  NOTHING IS DROPPED. NOTHING IS RE-INGESTED.")
        print()
        command.stamp(cfg, INITIAL_REVISION)

        print("  Now applying the migrations that actually have work to do:")
        print("    - auth hardening (lockout + password rotation columns)")
        print("    - server defaults (so FUTURE columns can be added to a")
        print("      populated table without an IntegrityError)")
        print()
        command.upgrade(cfg, "head")

    engine.dispose()

    # Verify.
    from backend.app.schema import schema_is_current

    ok, msg = schema_is_current()
    print()
    print("=" * 74)
    if ok:
        print(f"  DONE. {msg}")
        print()
        print("  Your data is untouched. Verify:")
        print("      python -m scripts.build_features")
        print("      python -m scripts.train_detect")
    else:
        print(f"  FAILED: {msg}")
        return 1
    print("=" * 74)
    return 0


if __name__ == "__main__":
    sys.exit(main())