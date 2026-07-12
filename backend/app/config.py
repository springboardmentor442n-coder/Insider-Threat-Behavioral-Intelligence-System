"""Application configuration.

Every setting the app needs is declared here as a typed field. Values are read
from environment variables (or the .env file) at startup and validated by
Pydantic.

Why not just call os.getenv() wherever we need a value?
  1. Typos fail silently. os.getenv("DATBASE_URL") returns None and the app
     crashes later with a confusing error, far from the real cause.
  2. No types. Everything from os.getenv() is a string; DEBUG="false" is a
     truthy string, so `if DEBUG:` would be True. A classic production bug.
  3. No validation. A missing DATABASE_URL should stop the app immediately at
     boot with a clear message - not 20 minutes later on the first request.

Pydantic Settings gives us fail-fast, typed, self-documenting config.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All application settings, read from the environment / .env file."""

    # --- Application ---------------------------------------------------------
    APP_NAME: str = "Insider Threat Behavioral Intelligence System"
    APP_ENV: str = "development"
    DEBUG: bool = False

    # --- Database ------------------------------------------------------------
    # No default: if this is missing the app MUST refuse to start rather than
    # silently fall back to some other database.
    DATABASE_URL: str

    # --- Data ----------------------------------------------------------------
    CERT_DATA_DIR: str = "data"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # tolerate unrelated vars in the environment
    )


@lru_cache
def get_settings() -> Settings:
    """Return the settings singleton.

    @lru_cache means the .env file is parsed exactly once per process, not on
    every request. FastAPI calls this as a dependency, so without the cache we
    would re-read the file on every single HTTP call.
    """
    return Settings()