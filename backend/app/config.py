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

    # Print every SQL statement to the console.
    #
    # Deliberately SEPARATE from DEBUG. Tying them together was a mistake: it
    # meant enabling the API docs also echoed 2.6 million INSERTs during
    # ingestion, which slowed the load dramatically and buried the actual
    # progress output. Defaults to off. Turn it on when you are debugging a
    # specific query, not as a side effect of being in development.
    SQL_ECHO: bool = False

    # --- Database ------------------------------------------------------------
    # No default: if this is missing the app MUST refuse to start rather than
    # silently fall back to some other database.
    DATABASE_URL: str

    # --- Security ------------------------------------------------------------
    # Signs every JWT. If this leaks, an attacker can mint a token claiming any
    # role they like - including administrator. It has NO default on purpose:
    # a default secret key is a backdoor that ships to production.
    # Generate one with:  python -c "import secrets; print(secrets.token_hex(32))"
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"

    # Short-lived by design. A JWT cannot be revoked before it expires, so a
    # deactivated account or a downgraded role stays valid until the token dies.
    # 30 minutes bounds that window.
    # Fifteen minutes, not thirty.
    #
    # This is the blast radius of a STOLEN access token. It is sent on every single
    # request, so it is the token most likely to leak - into a log, a proxy, a
    # browser extension, an error report. Fifteen minutes of exposure instead of
    # thirty halves that risk, and it costs the user nothing because the refresh
    # token renews it silently.
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15

    # Seven days. This is how long a user can go without re-entering their password.
    #
    # The refresh token is sent RARELY (only to /refresh), so it leaks far less
    # readily - and unlike the access token, it can be revoked, which is what makes
    # /logout mean something.
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Rate limiting. ON in production, OFF in the test suite.
    #
    # Not because the limits are inconvenient - because a test suite that creates
    # forty accounts and logs in sixty times is not the traffic the limits exist to
    # stop, and a test that fails at 3pm because it ran too soon after the last one
    # is a test nobody trusts.
    #
    # The limits themselves ARE tested, deliberately and in isolation, in
    # test_ratelimit.py. Turning a security control off for the tests and then never
    # testing it is how security controls quietly stop working.
    RATE_LIMIT_ENABLED: bool = True

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