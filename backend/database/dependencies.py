"""FastAPI database dependencies."""

from collections.abc import Generator

from sqlalchemy.orm import Session

from backend.database.session import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """Yield a SQLAlchemy session for request-scoped database access."""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
