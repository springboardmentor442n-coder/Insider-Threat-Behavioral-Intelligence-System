from fastapi import FastAPI
from fastapi import status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# =============================================================================
# Import API Routers
# =============================================================================

from backend.api.auth import router as auth_router
from backend.api.dashboard import router as dashboard_router
from backend.api.employees import router as employees_router
from backend.api.analytics import router as analytics_router
from backend.api.models import router as models_router
from backend.api.explainability import router as explainability_router
from backend.api.reports import router as reports_router
from backend.api.threats import router as threats_router
from backend.api.investigation import router as investigation_router
from backend.api.notifications import router as notifications_router
from backend.api.verification import router as verification_router
from backend.api.threat_analysis import router as threat_analysis_router
from backend.api import activity
from backend.api import risk

from backend.database import check_database_connection
from backend.settings import settings

# =============================================================================
# FastAPI Application
# =============================================================================

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=settings.app_description,
)

app.state.database_available = False
app.state.database_error = "Database connectivity not checked yet"

# =============================================================================
# CORS Configuration
# =============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods_list,
    allow_headers=settings.cors_allow_headers_list,
)

# =============================================================================
# Root Endpoint
# =============================================================================

@app.get("/")
def root():
    return {
        "message": "Insider Threat Behavioral Intelligence System API",
        "status": "Running",
    }


import uuid
import time
import logging
from fastapi import Request

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("sentinel_ai")

@app.middleware("http")
async def structured_logging_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    start_time = time.time()
    
    response = await call_next(request)
    
    duration_ms = round((time.time() - start_time) * 1000, 2)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Response-Time-Ms"] = str(duration_ms)
    
    logger.info(
        f"event=api_request request_id={request_id} method={request.method} "
        f"path={request.url.path} status={response.status_code} duration_ms={duration_ms}"
    )
    return response

# =============================================================================
# Health & Readiness Checks
# =============================================================================

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/ready")
def ready():
    return {
        "status": "ready",
        "database_available": getattr(app.state, "database_available", True),
    }


@app.on_event("startup")
def verify_database_on_startup() -> None:
    """Check database connectivity without blocking application startup."""

    is_available, message = check_database_connection()

    app.state.database_available = is_available
    app.state.database_error = message


@app.get("/health/database")
def database_health():
    """Return the current database connectivity status."""

    is_available, message = check_database_connection()

    app.state.database_available = is_available
    app.state.database_error = message

    payload = {
        "status": "healthy" if is_available else "unavailable",
        "database": {
            "available": is_available,
            "message": message,
        },
    }

    if is_available:
        return payload

    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content=payload,
    )


# =============================================================================
# Register Routers
# =============================================================================

# Authentication
app.include_router(
    auth_router,
    prefix="/auth",
    tags=["Authentication"],
)

# Dashboard
app.include_router(
    dashboard_router,
    prefix="/dashboard",
    tags=["Dashboard"],
)

# Notifications
app.include_router(
    notifications_router,
    prefix="/notifications",
    tags=["Notifications"],
)

# Employees
app.include_router(
    employees_router,
    prefix="/employees",
    tags=["Employees"],
)

# Models
app.include_router(
    models_router,
)

# Explainability
app.include_router(
    explainability_router,
    prefix="/explainability",
    tags=["Explainability"],
)

# Reports
app.include_router(
    reports_router,
    prefix="/reports",
    tags=["Reports"],
)

# Threat Center
app.include_router(
    threats_router,
    prefix="/threats",
    tags=["Threat Center"],
)

# =============================================================================
# Routers That Already Define Their Own Prefix
# =============================================================================

# Investigation -> prefix="/investigation" defined inside investigation.py
app.include_router(
    investigation_router,
)

# Analytics -> prefix="/analytics" defined inside analytics.py
app.include_router(
    analytics_router,
)

# Activity -> prefix="/activity" defined inside activity.py
app.include_router(
    activity.router,
)

# Risk -> prefix="/risk" defined inside risk.py
app.include_router(
    risk.router,
)

# Verification -> prefix="/verification" defined inside verification.py
app.include_router(
    verification_router,
)

# Threat Analysis -> prefix="/threat-analysis" defined inside threat_analysis.py
app.include_router(
    threat_analysis_router,
)

