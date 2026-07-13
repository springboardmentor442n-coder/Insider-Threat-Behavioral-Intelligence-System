"""Alembic environment.

WHY THIS FILE EXISTS AT ALL
--------------------------
Before Alembic, schema changes were applied with `Base.metadata.create_all()`.
That function creates tables that do not exist. It does NOT alter tables that do.

So every time a column was added to an existing model, the code was correct, the
database was stale, and the failure surfaced only at INSERT time:

    psycopg2.errors.UndefinedColumn:
      column "session_count" of relation "daily_features" does not exist

That happened TWICE in this project - once when http_daily_summary gained
`wikileaks_visits` (after seven minutes of streaming 13.9 GB of http.csv), and
again when daily_features gained `session_count`. The workaround both times was to
DROP the table and rebuild it. That works for DERIVED tables and is catastrophic
for anything else: you cannot drop `employees` to add a column to it.

Alembic fixes this properly. Schema changes become versioned, reviewable migration
files that ALTER in place. The database carries a version number. `alembic upgrade
head` moves it forward; `alembic downgrade -1` moves it back. Nothing is dropped,
nothing is lost, and the change is in git where someone can read it.

TWO THINGS THIS FILE DOES DIFFERENTLY FROM THE ALEMBIC TEMPLATE
---------------------------------------------------------------
1. The database URL comes from OUR settings object, not from alembic.ini. There is
   exactly one place the connection string lives, and that is the .env file. Two
   sources of truth for a database URL is how you migrate production by accident.

2. EVERY model module is imported below. Alembic autogenerates by diffing
   Base.metadata against the live database - and a model class that was never
   imported is not ON Base.metadata. It would be invisible, and autogenerate would
   cheerfully write a migration that DROPS its table, having concluded nobody
   wanted it any more. An unimported model is more dangerous than a missing one.
"""

from __future__ import annotations

from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

from backend.app.config import get_settings
from backend.app.database import Base

# LOAD-BEARING IMPORT - see the note above. Do not "clean this up".
from backend.app import features_models, models  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Override alembic.ini with the real, single source of truth.
settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Emit SQL to stdout instead of executing it.

    This is how schema changes reach production in most serious organisations: a
    DBA reads the SQL before anyone runs it.
    """
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Apply migrations directly against the database."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # compare_type catches a column whose TYPE changed, not merely its
            # existence. Without it, Integer -> Float is invisible to autogenerate,
            # and you discover the silent truncation in production.
            compare_type=True,
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()