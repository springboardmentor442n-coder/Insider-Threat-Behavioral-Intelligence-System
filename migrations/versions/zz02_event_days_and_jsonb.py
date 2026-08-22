"""malicious event days (the second labelling convention) + JSON -> JSONB

Revision ID: zz02eventdays
Revises: 21faf58d595b
Create Date: 2026-07-13

HAND-WRITTEN, BECAUSE AUTOGENERATE COULD NOT DO IT.

Alembic compares server defaults. To compare the OLD json column's default against
the NEW jsonb one it emits:

    SELECT '{}'::json = '{}'::jsonb

...and Postgres has no operator for that. The type change is the very thing being
compared, so autogenerate deadlocks on it:

    ProgrammingError: operator does not exist: json = jsonb

Which is a fair illustration of why the JSON -> JSONB change is worth making at all:
Postgres's `json` type stores raw TEXT and has NO EQUALITY OPERATOR. It cannot be
compared, cannot be indexed usefully, and - as here - it breaks the migration tool.
`jsonb` stores parsed binary and supports all three.

WHAT THIS MIGRATION DOES
------------------------
1. malicious_event_days - the days attacks ACTUALLY happened, from CERT's per-insider
   answer files. The existing labels come from insiders.csv, which gives each insider
   a WINDOW; labelling every day in the window as malicious yields 1,892 malicious
   user-days. Counting only the days on which a malicious event occurred yields 966 -
   and 966 is what the published literature reports. 49% of our "malicious" days
   contain no malicious activity.

2. daily_features.has_malicious_event - the second label, alongside the first. Both
   are kept, both are reported. Neither is a lie; a recall figure quoted without
   saying which convention produced it is simply not comparable to anything.

3. alerts.components / top_features -> jsonb.
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "zz02eventdays"
down_revision = "21faf58d595b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "malicious_event_days",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.String(length=20), nullable=False),
        sa.Column("event_date", sa.Date(), nullable=False),
        sa.Column("scenario", sa.Integer(), nullable=False),
        sa.Column("event_count", sa.Integer(), server_default="0", nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "event_date", name="uq_malicious_event_day"),
    )
    op.create_index("ix_malicious_event_days_user_id", "malicious_event_days", ["user_id"])
    op.create_index("ix_malicious_event_days_event_date", "malicious_event_days", ["event_date"])
    op.create_index("ix_malicious_event_days_scenario", "malicious_event_days", ["scenario"])

    op.add_column(
        "daily_features",
        sa.Column(
            "has_malicious_event",
            sa.Boolean(),
            server_default="false",
            nullable=False,
        ),
    )
    op.create_index(
        "ix_daily_features_has_malicious_event", "daily_features", ["has_malicious_event"]
    )

    # USING is mandatory. Without it Postgres refuses:
    #   column "components" cannot be cast automatically to type jsonb
    op.execute(
        "ALTER TABLE alerts ALTER COLUMN components TYPE jsonb USING components::jsonb"
    )
    op.execute(
        "ALTER TABLE alerts ALTER COLUMN top_features TYPE jsonb USING top_features::jsonb"
    )
    op.execute("ALTER TABLE alerts ALTER COLUMN components SET DEFAULT '{}'::jsonb")
    op.execute("ALTER TABLE alerts ALTER COLUMN top_features SET DEFAULT '[]'::jsonb")


def downgrade() -> None:
    op.execute("ALTER TABLE alerts ALTER COLUMN components DROP DEFAULT")
    op.execute("ALTER TABLE alerts ALTER COLUMN top_features DROP DEFAULT")
    op.execute(
        "ALTER TABLE alerts ALTER COLUMN components TYPE json USING components::json"
    )
    op.execute(
        "ALTER TABLE alerts ALTER COLUMN top_features TYPE json USING top_features::json"
    )
    op.drop_index("ix_daily_features_has_malicious_event", table_name="daily_features")
    op.drop_column("daily_features", "has_malicious_event")
    op.drop_index("ix_malicious_event_days_scenario", table_name="malicious_event_days")
    op.drop_index("ix_malicious_event_days_event_date", table_name="malicious_event_days")
    op.drop_index("ix_malicious_event_days_user_id", table_name="malicious_event_days")
    op.drop_table("malicious_event_days")