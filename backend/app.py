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

# =============================================================================
# Health Check
# =============================================================================

@app.get("/health")
def health():
    return {
        "status": "healthy",
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

# Employees
app.include_router(
    employees_router,
    prefix="/employees",
    tags=["Employees"],
)

# Models
app.include_router(
    models_router,
    prefix="/models",
    tags=["Models"],
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

#Threat
app.include_router(
    threats_router,
    prefix="/threats",
    tags=["Threat Center"],
)

# =============================================================================
# Routers that already define their own prefix
# =============================================================================

# Analytics -> prefix="/analytics" is already inside analytics.py
app.include_router(analytics_router)

# Activity -> prefix="/activity" is already inside activity.py
app.include_router(activity.router)

# Risk -> prefix="/risk" is already inside risk.py
app.include_router(risk.router)
