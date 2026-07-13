"""ensure server defaults on every NOT NULL column

Revision ID: zz01servdef
Revises: 0e25a229f190
Create Date: 2026-07-13

WHY THIS MIGRATION EXISTS
-------------------------
A database created by the OLD `Base.metadata.create_all()` path has NO server-side
defaults, because the models used `default=0` - a PYTHON-side default that the ORM
applies at insert time. The database column itself had no DEFAULT clause at all.

That matters for exactly one reason, and it is a big one:

    ALTER TABLE daily_features ADD COLUMN new_thing INTEGER NOT NULL

succeeds on an EMPTY table and FAILS on a populated one:

    IntegrityError: column "new_thing" contains null values

...because the 330,452 existing rows would all be NULL in the new column. So on a
fresh dev database every future migration passes, and on the real database with real
data every future migration fails. That is the worst possible failure mode: it looks
fine right up until it is expensive.

A database created FROM the initial migration already has these defaults, so this is
a no-op there. A database ADOPTED from the old create_all() world does not, and this
fixes it. ALTER COLUMN ... SET DEFAULT is idempotent, so it is safe either way.

WHY THE LIST IS GENERATED, NOT TYPED
------------------------------------
The first version of this migration had a HAND-WRITTEN list of columns. It covered
15. The models declare 58. It missed every column on http_daily_summary and every
column on user_baselines, and the test caught it only on a real database.

A list a human maintains is a list a human forgets to update. So this list is
GENERATED from Base.metadata and baked in as a literal - the migration stays a
self-contained, immutable snapshot, which is what a migration has to be, but it
cannot be incomplete.

test_migration_covers_every_server_default() asserts the two still agree. If someone
adds a column with a server_default and does not update this, CI fails.
"""

from alembic import op

revision = "zz01servdef"
down_revision = "0e25a229f190"
branch_labels = None
depends_on = None

# (table, column, default) - GENERATED from Base.metadata. Do not hand-edit.
SERVER_DEFAULTS = [
    ("audit_logs", "timestamp", "now()"),
    ("daily_features", "after_hours_logon_count", "0"),
    ("daily_features", "after_hours_usb_count", "0"),
    ("daily_features", "cloud_storage_visits", "0"),
    ("daily_features", "distinct_domains", "0"),
    ("daily_features", "distinct_pcs", "0"),
    ("daily_features", "doc_file_count", "0"),
    ("daily_features", "email_count", "0"),
    ("daily_features", "exe_file_count", "0"),
    ("daily_features", "external_email_count", "0"),
    ("daily_features", "file_event_count", "0"),
    ("daily_features", "hacking_site_visits", "0"),
    ("daily_features", "http_total_visits", "0"),
    ("daily_features", "is_malicious", "false"),
    ("daily_features", "job_site_visits", "0"),
    ("daily_features", "logon_count", "0"),
    ("daily_features", "max_recipients", "0"),
    ("daily_features", "new_pc_count", "0"),
    ("daily_features", "session_count", "0"),
    ("daily_features", "total_attachments", "0"),
    ("daily_features", "total_email_size", "0"),
    ("daily_features", "total_session_hours", "0"),
    ("daily_features", "usb_connect_count", "0"),
    ("daily_features", "used_supervisor_pc", "false"),
    ("daily_features", "weekend_logon_count", "0"),
    ("daily_features", "weekend_usb_count", "0"),
    ("daily_features", "wikileaks_visits", "0"),
    ("daily_features", "zip_file_count", "0"),
    ("email_events", "attachment_count", "0"),
    ("email_events", "has_external_recipient", "false"),
    ("email_events", "recipient_count", "0"),
    ("email_events", "size", "0"),
    ("employees", "is_insider", "false"),
    ("http_daily_summary", "cloud_storage_visits", "0"),
    ("http_daily_summary", "distinct_domains", "0"),
    ("http_daily_summary", "hacking_site_visits", "0"),
    ("http_daily_summary", "job_site_visits", "0"),
    ("http_daily_summary", "total_visits", "0"),
    ("http_daily_summary", "wikileaks_visits", "0"),
    ("security_users", "created_at", "now()"),
    ("security_users", "failed_login_attempts", "0"),
    ("security_users", "is_active", "true"),
    ("security_users", "password_changed_at", "now()"),
    ("user_baselines", "ever_used_usb", "false"),
    ("user_baselines", "ever_worked_after_hours", "false"),
    ("user_baselines", "mean_after_hours_logon", "0"),
    ("user_baselines", "mean_external_email", "0"),
    ("user_baselines", "mean_file_events", "0"),
    ("user_baselines", "mean_http_visits", "0"),
    ("user_baselines", "mean_logon_count", "0"),
    ("user_baselines", "mean_usb_connect", "0"),
    ("user_baselines", "std_after_hours_logon", "0"),
    ("user_baselines", "std_external_email", "0"),
    ("user_baselines", "std_file_events", "0"),
    ("user_baselines", "std_http_visits", "0"),
    ("user_baselines", "std_logon_count", "0"),
    ("user_baselines", "std_usb_connect", "0"),
    ("user_baselines", "training_days", "0"),
]


def upgrade() -> None:
    conn = op.get_bind()
    for table, column, default in SERVER_DEFAULTS:
        conn.exec_driver_sql(
            f'ALTER TABLE {table} ALTER COLUMN {column} SET DEFAULT {default}'
        )


def downgrade() -> None:
    conn = op.get_bind()
    for table, column, _default in SERVER_DEFAULTS:
        conn.exec_driver_sql(
            f'ALTER TABLE {table} ALTER COLUMN {column} DROP DEFAULT'
        )