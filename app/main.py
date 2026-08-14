from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
import time

from app.core.config import settings
from app.core.database import create_db_and_tables, check_db_connection
from app.api.v1 import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──────────────────────────────────────────────────────────
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")

    if check_db_connection():
        logger.info("MySQL connection OK")
        create_db_and_tables()
    else:
        logger.error("MySQL connection FAILED — check .env")

    # Auto-load ML model artifacts on startup
    try:
        from app.ml import inference as inf_service
        inf_service.load_model()
    except Exception as e:
        logger.warning(f"ML model load skipped: {e}")

    # Generate synthetic sample CSV files
    try:
        from scripts.generate_synthetic_csvs import generate_csvs
        generate_csvs()
    except Exception as e:
        logger.warning(f"Synthetic CSV generation skipped: {e}")

    # Auto-seed 300 synthetic employee cohort if not present or legacy LDAP count
    try:
        from app.core.database import SessionLocal
        from app.models import Employee
        db = SessionLocal()
        emp_count = db.query(Employee).count()
        db.close()
        if emp_count != 300:
            logger.info(f"Database employee count ({emp_count}) != 300. Seeding 300 synthetic cohort...")
            from scripts.seed_synthetic_300 import seed_synthetic_300
            seed_synthetic_300()
    except Exception as e:
        logger.warning(f"Auto-seeding synthetic cohort skipped: {e}")

    # Launch real-time simulation background worker
    import asyncio
    from app.services.simulation import run_simulation_loop
    sim_task = asyncio.create_task(run_simulation_loop())

    yield
    # ── Shutdown ─────────────────────────────────────────────────────────
    logger.info("Shutting down...")
    sim_task.cancel()
    try:
        await sim_task
    except asyncio.CancelledError:
        pass



app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
## Insider Threat Behavioral Intelligence System API

AI-powered platform for continuous employee activity monitoring, behavioral
anomaly detection, insider risk scoring, and threat investigation.

### ML Model
- **BehavioralIntelligenceNet** — PyTorch neural network (29 features → 5 threat classes)
- **Classes**: Data Exfiltration | IT Sabotage | Intellectual Property Theft | Normal | Unauthorized Access
- **Pipeline**: Feature Engineering → StandardScaler → Neural Network → LabelEncoder

### Modules
- **Auth** — JWT + OAuth2, RBAC
- **Employees** — Identity & profile management
- **Activities** — Log ingestion, CERT r4.2 CSV upload
- **Anomalies** — Isolation Forest + Z-score detection
- **Risk Scoring** — Weighted 5-factor insider risk score
- **ML Inference** — BehavioralIntelligenceNet threat classification
- **Alerts** — Severity-tiered alert lifecycle
- **Incidents** — Investigation with timeline reconstruction
- **Dashboard** — Role-specific dashboards
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Process-Time"] = f"{(time.perf_counter() - start)*1000:.1f}ms"
    return response

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.url}: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

app.include_router(api_router, prefix=settings.API_V1_STR)

from fastapi import WebSocket, WebSocketDisconnect
from app.core.websockets import manager

@app.websocket("/api/v1/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Maintain connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket session error: {e}")
        manager.disconnect(websocket)

@app.get("/health", tags=["Health"])
def health_check():
    from app.ml import inference as inf_service
    db_ok    = check_db_connection()
    model_ok = inf_service.is_model_loaded()
    return {
        "status":       "healthy" if (db_ok and model_ok) else "degraded",
        "version":      settings.APP_VERSION,
        "database":     "connected"    if db_ok    else "disconnected",
        "ml_model":     "loaded"       if model_ok else "not_loaded",
        "model_name":   "BehavioralIntelligenceNet",
        "n_classes":    5,
        "threat_classes": ["Data Exfiltration","IT Sabotage",
                           "Intellectual Property Theft","Normal","Unauthorized Access"],
    }

@app.get("/", tags=["Root"])
def root():
    return {
        "name":    settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs":    "/docs",
        "health":  "/health",
        "api":     settings.API_V1_STR,
    }
