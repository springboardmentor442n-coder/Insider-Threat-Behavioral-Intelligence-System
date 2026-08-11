"""Persistence foundation for the backend.

This package provides the SQLAlchemy engine, session factory, declarative base,
and FastAPI dependencies required for future persistence work.
"""

from backend.database.base import Base
from backend.database.database import check_database_connection, engine
from backend.database.dependencies import get_db
from backend.database.session import SessionLocal

__all__ = [
    "Base",
    "SessionLocal",
    "check_database_connection",
    "engine",
    "get_db",
]
"""Persistence foundation for the backend.

This package provides the SQLAlchemy engine, session factory, declarative base,
and FastAPI dependencies required for future persistence work.
"""

from backend.database.base import Base
from backend.database.database import check_database_connection, engine
from backend.database.dependencies import get_db
from backend.database.session import SessionLocal

__all__ = [
    "Base",
    "SessionLocal",
    "check_database_connection",
    "engine",
    "get_db",
]
