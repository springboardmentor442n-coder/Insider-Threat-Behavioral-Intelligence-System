"""
Database engine and connectivity helpers.

This module initializes the shared SQLAlchemy engine using the centralized
DATABASE_URL setting. It does not create tables or own any ORM models yet.
"""

from __future__ import annotations

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from backend.settings import settings
from backend.database.base import Base
import backend.database.models
import backend.database.notification_model

engine: Engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=1800,
    future=True,
)
# ============================================================
# Create all database tables
# ============================================================

Base.metadata.create_all(bind=engine)

def check_database_connection() -> tuple[bool, str]:
    """
    Verify that the configured database is reachable.

    Returns:
        tuple[bool, str]:
            (True, message) if the database is reachable,
            (False, error_message) otherwise.
    """
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return True, "Database connection successful"

    except SQLAlchemyError as exc:
        return False, str(exc)

    except Exception as exc:
        return False, str(exc)
