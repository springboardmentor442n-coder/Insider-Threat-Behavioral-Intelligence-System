from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool
from app.core.config import settings
from loguru import logger

# ─── Engine ───────────────────────────────────────────────────────────────────
engine = create_engine(
    settings.db_url,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,          # reconnect on stale connections
    pool_recycle=3600,           # recycle connections every hour
    echo=settings.DEBUG,
)

# Keep MySQL connection alive
@event.listens_for(engine, "connect")
def set_mysql_options(dbapi_conn, _):
    cursor = dbapi_conn.cursor()
    cursor.execute("SET SESSION time_zone = '+00:00'")
    cursor.execute("SET SESSION sql_mode = 'STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO'")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency — yields a DB session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_db_and_tables():
    """Create all tables (called at startup)."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("MySQL database tables created successfully.")
    except Exception as e:
        logger.error(f"Failed to create tables: {e}")
        raise


def check_db_connection() -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"DB connection check failed: {e}")
        return False
