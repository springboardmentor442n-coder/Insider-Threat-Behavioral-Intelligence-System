"""
Database session factory.

Provides a centralized SQLAlchemy session factory for the application.
"""

from typing import Generator

from sqlalchemy.orm import Session, sessionmaker

from backend.database.database import engine

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a SQLAlchemy database session.
    """
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()
        