"""FastAPI application entry point.

Phase 0 scope: prove the skeleton stands up.
  - the app boots
  - config loads and validates
  - the database is reachable
  - a test can assert all of the above

No authentication, no tables, no business logic yet. Those arrive in Phase 1+.
"""

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.config import get_settings
from backend.app.database import check_db_connection

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "UEBA platform that learns per-user behavioural baselines from activity "
        "logs, detects deviations, scores insider risk, and surfaces alerts for "
        "security analysts."
    ),
    version="0.1.0",
    # Interactive API docs are invaluable in development but expose your entire
    # API surface. In production they are switched off.
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
# The React frontend (Phase 7) runs on a different origin (port 5173) than the
# API (port 8000). Browsers block cross-origin requests unless the server
# explicitly allows them. We whitelist specific origins rather than using "*",
# because "*" would let ANY website call this API from a user's browser - not
# something you want on a security product.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Next.js dev server
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["meta"])
def root() -> dict[str, str]:
    """Basic service identification."""
    return {
        "service": settings.APP_NAME,
        "version": "0.1.0",
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
        "version": "0.1.0",
        "checks": {
            "api": "ok",
            "database": "ok" if database_ok else "unreachable",
        },
    }

    return JSONResponse(
        content=payload,
        status_code=(
            status.HTTP_200_OK
            if database_ok
            else status.HTTP_503_SERVICE_UNAVAILABLE
        ),
    )