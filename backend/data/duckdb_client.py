"""
DuckDB Singleton Connection
"""

from pathlib import Path

import duckdb


PROJECT_ROOT = Path(__file__).resolve().parents[1].parent

DATABASE_DIR = PROJECT_ROOT / "datasets"

_connection = None


def get_connection():

    global _connection

    if _connection is None:

        _connection = duckdb.connect()

    return _connection
