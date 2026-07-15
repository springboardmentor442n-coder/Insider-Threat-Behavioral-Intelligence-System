"""
===============================================================================
Module        : Feature Engineering
File          : 06_feature_engineering.py
Project       : Insider Threat Behavioral Intelligence System

Description:
    Generates behavioural features for every employee from the integrated
    CERT timeline dataset.

Input
------
datasets/integrated/employee_event_timeline.parquet
datasets/processed/psychometric.parquet

Output
-------
datasets/features/employee_features.parquet

Author
------
Nandan Kabra
===============================================================================
"""

from pathlib import Path
import logging
import duckdb

# =============================================================================
# Logging
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

# =============================================================================
# Paths
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INTEGRATED_DIR = PROJECT_ROOT / "datasets" / "integrated"

PROCESSED_DIR = PROJECT_ROOT / "datasets" / "processed"

FEATURE_DIR = PROJECT_ROOT / "datasets" / "features"

FEATURE_DIR.mkdir(
    parents=True,
    exist_ok=True
)

TIMELINE = INTEGRATED_DIR / "employee_event_timeline.parquet"

PSYCHOMETRIC = PROCESSED_DIR / "psychometric.parquet"

OUTPUT = FEATURE_DIR / "employee_features.parquet"

# =============================================================================
# Feature Engineering
# =============================================================================


class FeatureEngineering:

    def __init__(self):

        self.conn = duckdb.connect()

        logger.info("=" * 80)
        logger.info("FEATURE ENGINEERING")
        logger.info("=" * 80)

        logger.info(f"Timeline      : {TIMELINE}")
        logger.info(f"Psychometric  : {PSYCHOMETRIC}")

    # =========================================================================

    def generate_features(self):

        logger.info("Generating employee behavioural features...")

        query = f"""

COPY(

WITH base AS (

SELECT

    user,

    timestamp,

    pc,

    event_type,

    event_details,

    source,

    EXTRACT(HOUR FROM timestamp) AS hour,

    EXTRACT(DOW FROM timestamp) AS weekday,

    DATE(timestamp) AS event_date

FROM read_parquet('{TIMELINE.as_posix()}')

),

employee_activity AS (

SELECT

    user,

    COUNT(*) AS total_events,

    COUNT(DISTINCT event_date) AS active_days,

    COUNT(DISTINCT pc) AS unique_pcs,

    MIN(timestamp) AS first_activity,

    MAX(timestamp) AS last_activity,

    COUNT(DISTINCT source) AS unique_sources

FROM base

GROUP BY user

),

login_features AS (

SELECT

    user,

    COUNT(*) FILTER(

        WHERE event_type='LOGON'

    ) AS total_logins,

    COUNT(*) FILTER(

        WHERE hour < 6

    ) AS midnight_activity,

    COUNT(*) FILTER(

        WHERE hour>=18

    ) AS after_hours_activity,

    COUNT(*) FILTER(

        WHERE weekday IN (0,6)

    ) AS weekend_activity

FROM base

GROUP BY user

),

device_features AS (

SELECT

    user,

    COUNT(*) FILTER(

        WHERE event_type='DEVICE'

    ) AS device_events

FROM base

GROUP BY user

),

file_features AS (

SELECT

    user,

    COUNT(*) FILTER(

        WHERE event_type='FILE'

    ) AS file_events,

    COUNT(DISTINCT event_details)

        FILTER(

            WHERE event_type='FILE'

        ) AS unique_files

FROM base

GROUP BY user

),

email_features AS (

SELECT

    user,

    COUNT(*) FILTER(

        WHERE event_type='EMAIL'

    ) AS emails_sent

FROM base

GROUP BY user

),

http_features AS (

SELECT

    user,

    COUNT(*) FILTER(

        WHERE event_type='HTTP'

    ) AS web_events,

    COUNT(DISTINCT event_details)

        FILTER(

            WHERE event_type='HTTP'

        ) AS unique_urls

FROM base

GROUP BY user

),

time_features AS (

SELECT

    user,

    AVG(hour) AS average_hour,

    MIN(hour) AS earliest_hour,

    MAX(hour) AS latest_hour

FROM base

GROUP BY user

),

psychometric_features AS (

SELECT

    user_id AS user,

    O AS openness,

    C AS conscientiousness,

    E AS extraversion,

    A AS agreeableness,

    N AS neuroticism

FROM read_parquet(
    '{PSYCHOMETRIC.as_posix()}'
)

),

final_features AS (

SELECT

    ea.user,

    -- ==========================================================
    -- Overall Activity
    -- ==========================================================

    ea.total_events,

    ea.active_days,

    ea.unique_pcs,

    ea.unique_sources,

    ea.first_activity,

    ea.last_activity,

    -- ==========================================================
    -- Login Features
    -- ==========================================================

    COALESCE(lf.total_logins,0)
        AS total_logins,

    COALESCE(lf.midnight_activity,0)
        AS midnight_activity,

    COALESCE(lf.after_hours_activity,0)
        AS after_hours_activity,

    COALESCE(lf.weekend_activity,0)
        AS weekend_activity,

    -- ==========================================================
    -- Device Features
    -- ==========================================================

    COALESCE(df.device_events,0)
        AS device_events,

    -- ==========================================================
    -- File Features
    -- ==========================================================

    COALESCE(ff.file_events,0)
        AS file_events,

    COALESCE(ff.unique_files,0)
        AS unique_files,

    -- ==========================================================
    -- Email Features
    -- ==========================================================

    COALESCE(em.emails_sent,0)
        AS emails_sent,

    -- ==========================================================
    -- HTTP Features
    -- ==========================================================

    COALESCE(hf.web_events,0)
        AS web_events,

    COALESCE(hf.unique_urls,0)
        AS unique_urls,

    -- ==========================================================
    -- Time Features
    -- ==========================================================

    tf.average_hour,

    tf.earliest_hour,

    tf.latest_hour,

    -- ==========================================================
    -- Psychometric Features
    -- ==========================================================

    pf.openness,

    pf.conscientiousness,

    pf.extraversion,

    pf.agreeableness,

    pf.neuroticism

FROM employee_activity ea

LEFT JOIN login_features lf
ON ea.user = lf.user

LEFT JOIN device_features df
ON ea.user = df.user

LEFT JOIN file_features ff
ON ea.user = ff.user

LEFT JOIN email_features em
ON ea.user = em.user

LEFT JOIN http_features hf
ON ea.user = hf.user

LEFT JOIN time_features tf
ON ea.user = tf.user

LEFT JOIN psychometric_features pf
ON ea.user = pf.user

)

SELECT *

FROM final_features
)

TO '{OUTPUT.as_posix()}'

(FORMAT PARQUET);

"""

        logger.info("Executing Feature Engineering Query...")

        self.conn.execute(query)

        logger.info("Feature Engineering Completed Successfully.")

        logger.info(f"Saved : {OUTPUT}")

    # =======================================================================
    # Export Features
    # =======================================================================

    def export_features(self):

        logger.info("=" * 80)

        logger.info("VALIDATING GENERATED FEATURES")

        logger.info("=" * 80)

        result = self.conn.execute(f"""

        SELECT

            COUNT(*) AS employees,

            AVG(total_events) AS avg_events,

            MAX(total_events) AS max_events,

            MIN(total_events) AS min_events

        FROM read_parquet(

            '{OUTPUT.as_posix()}'

        )

        """).fetchone()

        logger.info(f"Employees : {result[0]:,}")

        logger.info(f"Average Events : {result[1]:.2f}")

        logger.info(f"Maximum Events : {result[2]:,.0f}")

        logger.info(f"Minimum Events : {result[3]:,.0f}")

    # =======================================================================
    # Summary
    # =======================================================================

    def summary(self):

        logger.info("=" * 80)

        logger.info("FEATURE SUMMARY")

        logger.info("=" * 80)

        df = self.conn.execute(f"""

        SELECT *

        FROM read_parquet(

            '{OUTPUT.as_posix()}'

        )

        LIMIT 5

        """).fetchdf()

        print()

        print(df)

        print()

        logger.info("=" * 80)
        # =============================================================================
# Main
# =============================================================================

def main():

    logger.info("=" * 80)
    logger.info("STARTING FEATURE ENGINEERING PIPELINE")
    logger.info("=" * 80)

    engine = FeatureEngineering()

    engine.generate_features()

    engine.export_features()

    engine.summary()

    logger.info("")
    logger.info("=" * 80)
    logger.info("FEATURE ENGINEERING COMPLETED SUCCESSFULLY")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()
    