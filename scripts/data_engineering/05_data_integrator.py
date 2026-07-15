"""
===============================================================================
Module        : Data Integrator
File          : 05_data_integrator.py
Project       : Insider Threat Behavioral Intelligence System

Description:
    Integrates all CERT datasets into one unified Employee Event Timeline.

Outputs:
    datasets/integrated/
        employee_event_timeline.parquet

Author:
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
# Project Paths
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROCESSED_DIR = PROJECT_ROOT / "datasets" / "processed"

RAW_DIR = PROJECT_ROOT / "datasets" / "raw" / "r4.2"

INTEGRATED_DIR = PROJECT_ROOT / "datasets" / "integrated"

INTEGRATED_DIR.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT_FILE = INTEGRATED_DIR / "employee_event_timeline.parquet"

# =============================================================================
# Data Integrator
# =============================================================================

class DataIntegrator:

    def __init__(self):

        self.conn = duckdb.connect()

    def integrate(self):

        logger.info("=" * 80)
        logger.info("BUILDING EMPLOYEE EVENT TIMELINE")
        logger.info("=" * 80)

        logger.info("Loading processed datasets...")

        query = f"""

        COPY(

            SELECT

                date AS timestamp,
                user,
                pc,
                'LOGON' AS event_type,
                activity AS event_details,
                'logon' AS source

            FROM read_parquet('{(PROCESSED_DIR/'logon.parquet').as_posix()}')

            UNION ALL

            SELECT

                date,
                user,
                pc,
                'DEVICE',
                activity,
                'device'

            FROM read_parquet('{(PROCESSED_DIR/'device.parquet').as_posix()}')

            UNION ALL

            SELECT

                date,
                user,
                pc,
                'EMAIL',
                content,
                'email'

            FROM read_parquet('{(PROCESSED_DIR/'email.parquet').as_posix()}')

            UNION ALL

            SELECT

                date,
                user,
                pc,
                'FILE',
                filename,
                'file'

            FROM read_parquet('{(PROCESSED_DIR/'file.parquet').as_posix()}')

            UNION ALL

            SELECT

    STRPTIME(
        date,
        '%m/%d/%Y %H:%M:%S'
    ) AS timestamp,

    user,

    pc,

    'HTTP' AS event_type,

    url AS event_details,

    'http' AS source

FROM read_csv_auto(

    '{(RAW_DIR/'http.csv').as_posix()}',

    types={{'date':'VARCHAR'}}

)

            ORDER BY timestamp

        )

        TO '{OUTPUT_FILE.as_posix()}'

        (FORMAT PARQUET);

        """

        logger.info("Integrating datasets...")

        self.conn.execute(query)

        logger.info("Employee Event Timeline Created Successfully")

        logger.info(f"Saved : {OUTPUT_FILE}")

    def summary(self):

        logger.info("=" * 80)

        logger.info("SUMMARY")

        logger.info("=" * 80)

        result = self.conn.execute(f"""

        SELECT COUNT(*)

        FROM read_parquet('{OUTPUT_FILE.as_posix()}')

        """).fetchone()[0]

        logger.info(f"Total Events : {result:,}")

        logger.info("=" * 80)


# =============================================================================
# Main
# =============================================================================

def main():

    integrator = DataIntegrator()

    integrator.integrate()

    integrator.summary()


if __name__ == "__main__":

    main()
