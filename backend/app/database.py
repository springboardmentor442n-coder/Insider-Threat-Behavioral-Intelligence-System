"""Database connectivity: engine, session factory, and a health probe.

Three things live here:

  engine   - the connection pool. Created ONCE for the whole process. Opening a
             new TCP connection to Postgres per request would be far too slow,
             so SQLAlchemy keeps a pool of live connections and hands them out.

  SessionLocal - a factory that produces short-lived Session objects. One
             session per request: it holds the transaction, and it must be
             closed afterwards or the connection leaks out of the pool.

  get_db() - the FastAPI dependency that opens a session, hands it to the
             endpoint, and guarantees it is closed even if the endpoint raises.
"""

from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from backend.app.config import get_settings

settings = get_settings()

# ---------------------------------------------------------------------------
# Engine (connection pool)
# ---------------------------------------------------------------------------
engine = create_engine(
    settings.DATABASE_URL,
    # pool_pre_ping tests a pooled connection with a cheap SELECT 1 before
    # handing it out. Without this, a connection that Postgres closed while
    # idle (restart, timeout, container bounce) gets handed to a request and
    # blows up. This is a small cost that prevents a whole class of flaky
    # "connection already closed" errors in production.
    pool_pre_ping=True,
    pool_size=5,          # steady-state connections kept open
    max_overflow=10,      # extra connections allowed under burst load
    echo=settings.DEBUG,  # log SQL in development only - never in production
)

# ---------------------------------------------------------------------------
# Session factory
# ---------------------------------------------------------------------------
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,  # we control transactions explicitly
    autoflush=False,   # no surprise writes mid-request
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base class every ORM model will inherit from.

    Empty for now - Phase 1 (users) and Phase 2 (activity logs) add real
    tables. Defining it here means every model shares one metadata registry,
    which is what lets us create/migrate all tables together.
    """


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a database session.

    The try/finally is the important part: whatever happens inside the endpoint
    - success, HTTP error, unhandled exception - the session is closed and its
    connection returned to the pool. Skipping this is how apps slowly exhaust
    their connection pool and fall over under load.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection() -> bool:
    """Return True if Postgres is reachable, False otherwise.

    Used by /health. We deliberately catch broad Exception here: the health
    endpoint's job is to report a boolean, not to crash. Any failure to reach
    the database - network, auth, DB down - means "not healthy".
    """
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception:
        return False