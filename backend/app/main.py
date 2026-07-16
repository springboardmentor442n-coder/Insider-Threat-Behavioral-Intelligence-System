"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from backend.app.config import get_settings
from backend.app.database import Base, check_db_connection, engine
from backend.app.ratelimit import limiter
from backend.app.routers import (
    entity,
    notifications,
    alerts,
    audit,
    auth,
    dashboard,
    data,
    investigate,
    users,
)
from backend.app.schema import schema_is_current

settings = get_settings()


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Verify the database schema before serving a single request.

    THIS USED TO CALL create_all(), AND THAT WAS THE BUG.

    `Base.metadata.create_all()` creates tables that do not exist. It does NOT alter
    tables that do. So when a model gained a column, startup was clean and the first
    INSERT died - once after seven minutes of streaming 13.9 GB of http.csv, once on
    session_count. Twice.

    Startup now VERIFIES that the database is at the migration the code expects, and
    REFUSES TO RUN if it is not.

    Refusing to boot is the correct behaviour, and it is not a lesser evil. An
    application that starts happily against the wrong schema fails LATER - in
    production, under load, on real data, with a stack trace that points at an INSERT
    rather than at the deployment that caused it. Failing at startup, with a message
    that says exactly which migration is missing, costs thirty seconds. Failing at the
    first INSERT costs an incident.
    """
    ok, message = schema_is_current()
    if not ok:
        raise RuntimeError(f"DATABASE SCHEMA IS OUT OF DATE.\n\n{message}\n")
    logger.info("Schema check passed: %s", message)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "UEBA platform that learns per-user behavioural baselines from activity "
        "logs, detects deviations, scores insider risk, and surfaces alerts for "
        "security analysts."
    ),
    version="0.2.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# The React frontend (Phase 7) runs on a different origin than the API.
# Origins are whitelisted explicitly rather than using "*", which would let ANY
# website call this API from a logged-in user's browser - not something you want
# on a security product.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting.
#
# The account lockout stops someone guessing ONE password. This stops PASSWORD
# SPRAYING - one password tried against a thousand accounts, which trips no lockout
# anywhere because each account sees exactly one failed login. The two defend
# against different attacks and neither replaces the other.
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.include_router(auth.router)
app.include_router(data.router)
app.include_router(users.router)
app.include_router(alerts.router)
app.include_router(investigate.router)
app.include_router(dashboard.router)
app.include_router(audit.router)
app.include_router(entity.router)
app.include_router(notifications.router)


@app.get("/", tags=["meta"])
def root() -> dict[str, str]:
    """Basic service identification."""
    return {
        "service": settings.APP_NAME,
        "version": "0.2.0",
        "environment": settings.APP_ENV,
        "status": "running",
    }


@app.get("/health", tags=["meta"])
def health_check() -> JSONResponse:
    """Liveness + readiness probe.

    A health check that only returns {"status": "ok"} is close to useless: the
    process being alive tells you nothing about whether it can actually serve
    traffic. An API that cannot reach its database is NOT healthy, even though
    the process is running fine.

    So this endpoint checks its critical dependency (Postgres) and returns
    503 SERVICE_UNAVAILABLE when that dependency is down. That is the signal a
    load balancer, Kubernetes probe, or uptime monitor needs to pull this
    instance out of rotation instead of routing traffic into a black hole.
    """
    database_ok = check_db_connection()

    payload = {
        "status": "healthy" if database_ok else "unhealthy",
        "service": settings.APP_NAME,
        "version": "0.2.0",
        "checks": {
            "api": "ok",
            "database": "ok" if database_ok else "unreachable",
        },
    }

    return JSONResponse(
        content=payload,
        status_code=(
            status.HTTP_200_OK if database_ok
            else status.HTTP_503_SERVICE_UNAVAILABLE
        ),
    )
