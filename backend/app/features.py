"""Phase 3: behavioural feature engineering and per-user baselines.

THE CENTRAL IDEA
----------------
Read the three r4.2 scenarios and one word keeps recurring:

  scenario 1  "a user who has NOT PREVIOUSLY used removable drives or worked
               after hours BEGINS doing both"
  scenario 2  "uses a thumb drive at MARKEDLY HIGHER RATES than their
               PREVIOUS activity"
  scenario 3  a sysadmin logs into a machine that is NOT HIS

None of these are absolute. Using a USB stick is not a crime; thousands of the
1,000 employees do it every week. What is anomalous is the CHANGE - the same
action, performed by someone who never performed it before.

That is why this module produces two things:

  daily_features  - what each person did on each day (the observation)
  user_baselines  - what that person NORMALLY does (the expectation)

Anomaly = observation far from expectation. Phase 4 does the comparison; this
module builds both sides of it.

WHY SQL AND NOT PANDAS
----------------------
There are 4.3 million events in Postgres. Pulling them into pandas to group them
would move ~2 GB across a socket, deserialise it into Python objects, and do in
minutes what the database does in seconds against its own indexes. Aggregation
belongs where the data already is. Pandas gets used later, for the small derived
table (~330k rows), where it is genuinely the right tool.
"""

from __future__ import annotations

import time

from sqlalchemy import delete, func, select, text
from sqlalchemy.orm import Session

from backend.app.features_models import DailyFeatures, UserBaseline
from backend.app.models import Employee

# "After hours" = before 07:00 or from 18:00 onward.
# CERT's synthetic employees keep office hours, so this cleanly separates the
# normal working day from the 02:00 activity the scenarios describe.
WORK_START_HOUR = 7
WORK_END_HOUR = 18

# The baseline is built from the FIRST 120 days only.
#
# This is the most important number in the file. Build the baseline over ALL
# time and the attack days get folded into the very average they are supposed to
# stand out from - the insider's USB spike raises his own "normal USB usage",
# and he looks less anomalous the worse he behaves. That is not a subtle bias;
# it is the model marking its own homework.
#
# CERT r4.2 runs Jan 2010 - May 2011. The earliest malicious window in the answer
# key starts well after day 120, so this training period is clean.
BASELINE_TRAINING_DAYS = 120


# ===========================================================================
# Daily features
# ===========================================================================

# Each CTE below computes one family of features at the (user, day) grain, and
# the final SELECT full-joins them together. A user with a logon but no email
# still needs a row - hence COALESCE everywhere, and a FULL OUTER JOIN rather
# than an inner one, which would silently drop those days.
_DAILY_FEATURES_SQL = text(f"""
WITH
-- The (user, pc) pairs and the first date each was ever seen. A PC appearing
-- for the first time on a given day is a "new PC" for that user on that day.
first_pc_use AS (
    SELECT user_id, pc, MIN(timestamp::date) AS first_date
    FROM logon_events
    GROUP BY user_id, pc
),
new_pcs AS (
    SELECT user_id, first_date AS day, COUNT(*) AS new_pc_count
    FROM first_pc_use
    GROUP BY user_id, first_date
),

-- Each employee's PRIMARY pc: the one they log into most often. Used to work
-- out whose machine is whose.
primary_pc AS (
    SELECT DISTINCT ON (user_id) user_id, pc
    FROM (
        SELECT user_id, pc, COUNT(*) AS uses
        FROM logon_events
        GROUP BY user_id, pc
    ) t
    ORDER BY user_id, uses DESC
),

-- The reporting line. employees.supervisor holds the supervisor's NAME, so we
-- self-join the roster on employee_name to resolve it to a user_id, then look
-- up that supervisor's primary PC.
supervisor_pc AS (
    SELECT e.user_id, p.pc AS boss_pc
    FROM employees e
    JOIN employees s ON e.supervisor = s.employee_name
    JOIN primary_pc p ON p.user_id = s.user_id
    WHERE e.supervisor IS NOT NULL
),

-- Session durations, from logon -> logoff pairs.
--
-- LEAD() looks at the next event for the same (user, pc) in time order. A Logon
-- immediately followed by a Logoff on the same machine is one session.
--
-- Sessions longer than 24h are DISCARDED: they are almost always a machine left
-- running over a weekend, not a person sitting at a desk for 30 hours. Including
-- them would let a forgotten screen-lock masquerade as suspicious dedication.
sessions AS (
    SELECT
        user_id,
        timestamp AS logon_ts,
        activity,
        LEAD(timestamp) OVER (
            PARTITION BY user_id, pc ORDER BY timestamp
        ) AS next_ts,
        LEAD(activity) OVER (
            PARTITION BY user_id, pc ORDER BY timestamp
        ) AS next_activity
    FROM logon_events
),
session_hours AS (
    SELECT
        user_id,
        logon_ts::date AS day,
        EXTRACT(EPOCH FROM (next_ts - logon_ts)) / 3600.0 AS hours
    FROM sessions
    WHERE activity = 'Logon'
      AND next_activity = 'Logoff'
      AND next_ts > logon_ts
      AND EXTRACT(EPOCH FROM (next_ts - logon_ts)) / 3600.0 < 24
),
session_daily AS (
    SELECT
        user_id,
        day,
        COUNT(*) AS session_count,
        SUM(hours) AS total_session_hours
    FROM session_hours
    GROUP BY user_id, day
),

logon AS (
    SELECT
        l.user_id,
        l.timestamp::date AS day,
        COUNT(*) FILTER (WHERE l.activity = 'Logon') AS logon_count,
        COUNT(*) FILTER (
            WHERE l.activity = 'Logon'
              AND (EXTRACT(HOUR FROM l.timestamp) < {WORK_START_HOUR}
                   OR EXTRACT(HOUR FROM l.timestamp) >= {WORK_END_HOUR})
        ) AS after_hours_logon_count,
        COUNT(*) FILTER (
            WHERE l.activity = 'Logon'
              AND EXTRACT(DOW FROM l.timestamp) IN (0, 6)   -- Sun, Sat
        ) AS weekend_logon_count,
        COUNT(DISTINCT l.pc) AS distinct_pcs,
        -- Did they log into their boss's machine today? Scenario 3's fingerprint.
        BOOL_OR(sp.boss_pc IS NOT NULL AND l.pc = sp.boss_pc) AS used_supervisor_pc
    FROM logon_events l
    LEFT JOIN supervisor_pc sp ON sp.user_id = l.user_id
    GROUP BY l.user_id, l.timestamp::date
),

device AS (
    SELECT
        user_id,
        timestamp::date AS day,
        COUNT(*) FILTER (WHERE activity = 'Connect') AS usb_connect_count,
        COUNT(*) FILTER (
            WHERE activity = 'Connect'
              AND (EXTRACT(HOUR FROM timestamp) < {WORK_START_HOUR}
                   OR EXTRACT(HOUR FROM timestamp) >= {WORK_END_HOUR})
        ) AS after_hours_usb_count,
        COUNT(*) FILTER (
            WHERE activity = 'Connect'
              AND EXTRACT(DOW FROM timestamp) IN (0, 6)
        ) AS weekend_usb_count
    FROM device_events
    GROUP BY user_id, timestamp::date
),

files AS (
    SELECT
        user_id,
        timestamp::date AS day,
        COUNT(*) AS file_event_count,
        COUNT(*) FILTER (WHERE file_extension = 'exe') AS exe_file_count,
        COUNT(*) FILTER (WHERE file_extension IN ('doc','docx','pdf','txt'))
            AS doc_file_count,
        COUNT(*) FILTER (WHERE file_extension IN ('zip','rar','7z'))
            AS zip_file_count
    FROM file_events
    GROUP BY user_id, timestamp::date
),

emails AS (
    SELECT
        user_id,
        timestamp::date AS day,
        COUNT(*) AS email_count,
        COUNT(*) FILTER (WHERE has_external_recipient) AS external_email_count,
        COALESCE(SUM(size), 0) AS total_email_size,
        COALESCE(SUM(attachment_count), 0) AS total_attachments,
        COALESCE(MAX(recipient_count), 0) AS max_recipients
    FROM email_events
    GROUP BY user_id, timestamp::date
),

web AS (
    SELECT
        user_id,
        date AS day,
        total_visits        AS http_total_visits,
        job_site_visits,
        wikileaks_visits,
        cloud_storage_visits,
        hacking_site_visits,
        distinct_domains
    FROM http_daily_summary
),

-- Every (user, day) that appears in ANY source. A day with only email activity
-- and no logon still needs a feature row.
all_days AS (
    SELECT user_id, day FROM logon
    UNION SELECT user_id, day FROM device
    UNION SELECT user_id, day FROM files
    UNION SELECT user_id, day FROM emails
    UNION SELECT user_id, day FROM web
    UNION SELECT user_id, day FROM session_daily
),

-- LABEL 1: the WINDOW. A day is malicious if it falls between the insider's start
-- and end in insiders.csv. Days outside the window - even for a known insider - are
-- normal behaviour and must be labelled as such, or we teach the model that
-- normality is malicious.
labels AS (
    SELECT DISTINCT d.user_id, d.day, TRUE AS is_malicious
    FROM all_days d
    JOIN insider_ground_truth g
      ON g.user_id = d.user_id
     AND d.day >= g.start_time::date
     AND d.day <= g.end_time::date
),

-- LABEL 2: the EVENT DAYS. A day is malicious only if a malicious event ACTUALLY
-- happened on it, per CERT's per-insider answer files.
--
-- These two labels disagree about 49% of the malicious days. The window convention
-- yields 1,892; the event convention yields 966 - and 966 is what the published
-- literature reports.
--
-- The disagreement is worst on scenario 1, which is a SINGLE-DAY exfiltration handed
-- a multi-week window: AAM0658 has seven window days and two real ones. We were being
-- scored for "missing" five days on which the man did nothing wrong, which is a large
-- part of why scenario-1 recall reads 73% and scenario-2 reads 97%.
--
-- Neither label is a lie. Both are reported. A recall figure quoted without saying
-- which convention produced it is not comparable to anything.
event_labels AS (
    SELECT DISTINCT m.user_id, m.event_date AS day, TRUE AS has_malicious_event
    FROM malicious_event_days m
)

SELECT
    a.user_id,
    a.day AS date,

    COALESCE(l.logon_count, 0)              AS logon_count,
    COALESCE(l.after_hours_logon_count, 0)  AS after_hours_logon_count,
    COALESCE(l.weekend_logon_count, 0)      AS weekend_logon_count,
    COALESCE(l.distinct_pcs, 0)             AS distinct_pcs,
    COALESCE(n.new_pc_count, 0)             AS new_pc_count,
    COALESCE(l.used_supervisor_pc, FALSE)   AS used_supervisor_pc,

    COALESCE(s.session_count, 0)            AS session_count,
    COALESCE(s.total_session_hours, 0.0)    AS total_session_hours,

    COALESCE(dv.usb_connect_count, 0)       AS usb_connect_count,
    COALESCE(dv.after_hours_usb_count, 0)   AS after_hours_usb_count,
    COALESCE(dv.weekend_usb_count, 0)       AS weekend_usb_count,

    COALESCE(f.file_event_count, 0)         AS file_event_count,
    COALESCE(f.exe_file_count, 0)           AS exe_file_count,
    COALESCE(f.doc_file_count, 0)           AS doc_file_count,
    COALESCE(f.zip_file_count, 0)           AS zip_file_count,

    COALESCE(e.email_count, 0)              AS email_count,
    COALESCE(e.external_email_count, 0)     AS external_email_count,
    COALESCE(e.total_email_size, 0)         AS total_email_size,
    COALESCE(e.total_attachments, 0)        AS total_attachments,
    COALESCE(e.max_recipients, 0)           AS max_recipients,

    COALESCE(w.http_total_visits, 0)        AS http_total_visits,
    COALESCE(w.job_site_visits, 0)          AS job_site_visits,
    COALESCE(w.wikileaks_visits, 0)         AS wikileaks_visits,
    COALESCE(w.cloud_storage_visits, 0)     AS cloud_storage_visits,
    COALESCE(w.hacking_site_visits, 0)      AS hacking_site_visits,
    COALESCE(w.distinct_domains, 0)         AS distinct_domains,

    COALESCE(lb.is_malicious, FALSE)        AS is_malicious,
    COALESCE(ev.has_malicious_event, FALSE) AS has_malicious_event

FROM all_days a
LEFT JOIN logon    l  ON l.user_id  = a.user_id AND l.day  = a.day
LEFT JOIN new_pcs  n  ON n.user_id  = a.user_id AND n.day  = a.day
LEFT JOIN session_daily s ON s.user_id = a.user_id AND s.day = a.day
LEFT JOIN device   dv ON dv.user_id = a.user_id AND dv.day = a.day
LEFT JOIN files    f  ON f.user_id  = a.user_id AND f.day  = a.day
LEFT JOIN emails   e  ON e.user_id  = a.user_id AND e.day  = a.day
LEFT JOIN web      w  ON w.user_id  = a.user_id AND w.day  = a.day
LEFT JOIN labels       lb ON lb.user_id = a.user_id AND lb.day = a.day
LEFT JOIN event_labels ev ON ev.user_id = a.user_id AND ev.day = a.day
""")


def build_daily_features(db: Session) -> int:
    """Compute daily_features for every user-day. Idempotent - clears first."""
    db.execute(delete(DailyFeatures))
    db.commit()

    rows = db.execute(_DAILY_FEATURES_SQL).mappings().all()

    batch: list[dict] = []
    total = 0
    for row in rows:
        batch.append(dict(row))
        if len(batch) >= 10_000:
            db.bulk_insert_mappings(DailyFeatures, batch)
            db.commit()
            total += len(batch)
            batch = []

    if batch:
        db.bulk_insert_mappings(DailyFeatures, batch)
        db.commit()
        total += len(batch)

    return total


# ===========================================================================
# Baselines
# ===========================================================================

_BASELINE_SQL = text(f"""
WITH
-- The training window: the first {BASELINE_TRAINING_DAYS} days of the dataset.
bounds AS (
    SELECT MIN(date) AS first_day,
           MIN(date) + INTERVAL '{BASELINE_TRAINING_DAYS} days' AS cutoff
    FROM daily_features
),
training AS (
    SELECT f.*
    FROM daily_features f, bounds b
    WHERE f.date < b.cutoff
      -- CONTAMINATION GUARD.
      --
      -- A chronological cutoff alone is NOT enough. If any attack begins inside
      -- the training window - and in r4.2 some do - then that insider's
      -- malicious days get folded into his own definition of "normal". His USB
      -- spike raises his own mean USB usage, his after-hours logons raise his own
      -- mean, and he ends up looking LESS anomalous the worse he behaves. The
      -- model would be grading itself on a curve it drew after seeing the answers.
      --
      -- So we also exclude every known-malicious day outright. The baseline is
      -- built strictly from behaviour we know was benign.
      --
      -- Is that "using the labels"? Yes - and it is the right call, for a reason
      -- worth being precise about: the baseline is not a MODEL, it is a
      -- DEFINITION of normal. In a real deployment you would build it from a
      -- historical period your SOC has already verified as clean, which is
      -- exactly the same operation. What we must never do is let the labels
      -- reach the DETECTOR, and they do not: is_malicious is never a feature,
      -- and Phase 4 evaluates on held-out days.
      AND NOT f.is_malicious
)
SELECT
    t.user_id,
    COUNT(*) AS training_days,
    e.department,
    e.role,

    -- STDDEV_SAMP returns NULL for a single row, so COALESCE to 0.
    AVG(t.logon_count)::float                       AS mean_logon_count,
    COALESCE(STDDEV_SAMP(t.logon_count), 0)::float  AS std_logon_count,

    AVG(t.after_hours_logon_count)::float                      AS mean_after_hours_logon,
    COALESCE(STDDEV_SAMP(t.after_hours_logon_count), 0)::float AS std_after_hours_logon,

    AVG(t.usb_connect_count)::float                       AS mean_usb_connect,
    COALESCE(STDDEV_SAMP(t.usb_connect_count), 0)::float  AS std_usb_connect,

    AVG(t.file_event_count)::float                       AS mean_file_events,
    COALESCE(STDDEV_SAMP(t.file_event_count), 0)::float  AS std_file_events,

    AVG(t.external_email_count)::float                      AS mean_external_email,
    COALESCE(STDDEV_SAMP(t.external_email_count), 0)::float AS std_external_email,

    AVG(t.http_total_visits)::float                      AS mean_http_visits,
    COALESCE(STDDEV_SAMP(t.http_total_visits), 0)::float AS std_http_visits,

    -- The "has this person EVER done X" flags that scenario 1 turns on.
    -- A z-score cannot express "never, and now suddenly" when the standard
    -- deviation is zero. A boolean can.
    BOOL_OR(t.usb_connect_count > 0)        AS ever_used_usb,
    BOOL_OR(t.after_hours_logon_count > 0)  AS ever_worked_after_hours

FROM training t
JOIN employees e ON e.user_id = t.user_id
GROUP BY t.user_id, e.department, e.role
""")


def build_baselines(db: Session) -> int:
    """Compute each user's behavioural baseline from clean training days."""
    db.execute(delete(UserBaseline))
    db.commit()

    rows = db.execute(_BASELINE_SQL).mappings().all()
    mappings = [dict(r) for r in rows]

    if mappings:
        db.bulk_insert_mappings(UserBaseline, mappings)
        db.commit()

    return len(mappings)


def check_baseline_contamination(db: Session) -> dict:
    """Report whether any attack days fall inside the chronological window.

    This exists because the first version of this module did NOT check, and the
    training window turned out to contain malicious days. Silent contamination is
    the worst kind of bug in an ML pipeline: nothing crashes, the numbers look
    plausible, and the model is quietly learning that the attack is normal.

    The guard in _BASELINE_SQL now excludes those days, so contamination is
    handled - but "handled" is not "invisible". If the window overlaps the
    attacks, we say so out loud, every run.
    """
    row = db.execute(text(f"""
        WITH bounds AS (
            SELECT MIN(date) AS first_day,
                   MIN(date) + INTERVAL '{BASELINE_TRAINING_DAYS} days' AS cutoff
            FROM daily_features
        )
        SELECT
            (SELECT first_day FROM bounds)                      AS data_starts,
            (SELECT cutoff FROM bounds)                         AS baseline_cutoff,
            (SELECT MIN(date) FROM daily_features
              WHERE is_malicious)                               AS first_attack_day,
            (SELECT COUNT(*) FROM daily_features f, bounds b
              WHERE f.date < b.cutoff)                          AS window_days,
            (SELECT COUNT(*) FROM daily_features f, bounds b
              WHERE f.date < b.cutoff AND f.is_malicious)       AS window_attack_days
    """)).mappings().one()

    d = dict(row)
    d["contaminated"] = (d["window_attack_days"] or 0) > 0
    return d


# ===========================================================================
# Orchestration + validation
# ===========================================================================


def recreate_feature_tables(engine) -> None:
    """DROP and rebuild daily_features + user_baselines. Nothing else.

    THIS EXISTS BECAUSE THE SAME BUG BIT TWICE.

    `Base.metadata.create_all()` creates tables that do not exist. It does NOT
    alter tables that already do. So when DailyFeatures gained `session_count` and
    `total_session_hours`, create_all() looked at the existing daily_features
    table, decided there was nothing to do, and the build died on the INSERT:

        column "session_count" of relation "daily_features" does not exist

    That is the second time this exact failure has happened - the first was
    http_daily_summary gaining wikileaks_visits, which cost seven minutes of
    streaming before it fell over. recreate_derived_tables() was written to fix
    that one, but it was only wired into the INGESTION script, so changing the
    feature schema walked straight back into it.

    The lesson is that a fix applied in one place is not a fix. So this is now
    unconditional: build_features ALWAYS drops and rebuilds its own output tables.
    That is what "build" means. A future column addition simply works, with nobody
    needing to remember anything.

    WHY THIS IS SAFE, AND WHY IT IS NARROWER THAN recreate_derived_tables():
      - daily_features and user_baselines are 100% DERIVED. Every row is recomputed
        from the raw event tables on every run. Dropping them loses nothing.
      - http_daily_summary is deliberately NOT touched here. It is derived too, but
        it is built during INGESTION by streaming 13.9 GB of http.csv - about seven
        and a half minutes. Dropping it would silently force a full re-ingest.

    (The grown-up answer is Alembic migrations, which version schema changes and
    ALTER in place. That remains a real gap, listed as a hardening item rather than
    waved away. But for tables that rebuild in under a minute, drop-and-recreate is
    honest, simple, and impossible to get wrong.)
    """
    # Drop and rebuild these two tables ONLY.
    #
    # Not create_all() - that would silently create any missing table, hiding the
    # fact that the database was never migrated. Alembic owns the schema. This
    # function owns the CONTENT of two derived tables, and nothing else.
    DailyFeatures.__table__.drop(engine, checkfirst=True)
    UserBaseline.__table__.drop(engine, checkfirst=True)

    DailyFeatures.__table__.create(engine, checkfirst=True)
    UserBaseline.__table__.create(engine, checkfirst=True)


def run_feature_engineering(db: Session) -> dict:
    """Build daily features, then baselines. Returns a summary."""
    started = time.perf_counter()

    feature_rows = build_daily_features(db)
    baseline_rows = build_baselines(db)

    return {
        "daily_feature_rows": feature_rows,
        "baseline_rows": baseline_rows,
        "duration_seconds": round(time.perf_counter() - started, 2),
    }


def validate_features(db: Session) -> dict:
    """Sanity-check the engineered features against the known r4.2 scenarios.

    This is the real test of whether feature engineering worked. If the features
    are correct, the insiders' malicious days should look VISIBLY different from
    everyone else's normal days - without a model, without training, just in the
    raw averages.

    If they do not, no amount of clever modelling downstream will save us. Better
    to find that out here, in a table you can read, than after training something
    that quietly learns nothing.
    """
    malicious = db.execute(text("""
        SELECT
            COUNT(*) AS days,
            ROUND(AVG(after_hours_logon_count)::numeric, 3) AS after_hours,
            ROUND(AVG(usb_connect_count)::numeric, 3)       AS usb,
            ROUND(AVG(file_event_count)::numeric, 3)        AS files,
            ROUND(AVG(job_site_visits)::numeric, 3)         AS job_sites,
            ROUND(AVG(wikileaks_visits)::numeric, 3)        AS wikileaks,
            ROUND(AVG(hacking_site_visits)::numeric, 3)     AS hacking_sites,
            ROUND(AVG(exe_file_count)::numeric, 3)          AS exe_files,
            ROUND(AVG(max_recipients)::numeric, 2)          AS max_recipients,
            ROUND(100.0 * AVG(used_supervisor_pc::int)::numeric, 2) AS pct_boss_pc
        FROM daily_features WHERE is_malicious
    """)).mappings().one()

    normal = db.execute(text("""
        SELECT
            COUNT(*) AS days,
            ROUND(AVG(after_hours_logon_count)::numeric, 3) AS after_hours,
            ROUND(AVG(usb_connect_count)::numeric, 3)       AS usb,
            ROUND(AVG(file_event_count)::numeric, 3)        AS files,
            ROUND(AVG(job_site_visits)::numeric, 3)         AS job_sites,
            ROUND(AVG(wikileaks_visits)::numeric, 3)        AS wikileaks,
            ROUND(AVG(hacking_site_visits)::numeric, 3)     AS hacking_sites,
            ROUND(AVG(exe_file_count)::numeric, 3)          AS exe_files,
            ROUND(AVG(max_recipients)::numeric, 2)          AS max_recipients,
            ROUND(100.0 * AVG(used_supervisor_pc::int)::numeric, 2) AS pct_boss_pc
        FROM daily_features WHERE NOT is_malicious
    """)).mappings().one()

    by_scenario = db.execute(text("""
        SELECT
            e.insider_scenario AS scenario,
            COUNT(*) AS malicious_days,
            ROUND(AVG(f.after_hours_logon_count)::numeric, 2) AS after_hours,
            ROUND(AVG(f.usb_connect_count)::numeric, 2)       AS usb,
            ROUND(AVG(f.job_site_visits)::numeric, 2)         AS job_sites,
            ROUND(AVG(f.wikileaks_visits)::numeric, 2)        AS wikileaks,
            ROUND(AVG(f.hacking_site_visits)::numeric, 2)     AS hacking_sites
        FROM daily_features f
        JOIN employees e ON e.user_id = f.user_id
        WHERE f.is_malicious
        GROUP BY e.insider_scenario
        ORDER BY e.insider_scenario
    """)).mappings().all()

    return {
        "malicious": dict(malicious),
        "normal": dict(normal),
        "by_scenario": [dict(r) for r in by_scenario],
    }


def get_feature_counts(db: Session) -> dict[str, int]:
    return {
        "daily_feature_rows": db.scalar(
            select(func.count()).select_from(DailyFeatures)
        ) or 0,
        "malicious_days": db.scalar(
            select(func.count()).select_from(DailyFeatures)
            .where(DailyFeatures.is_malicious)
        ) or 0,
        "baseline_rows": db.scalar(
            select(func.count()).select_from(UserBaseline)
        ) or 0,
    }