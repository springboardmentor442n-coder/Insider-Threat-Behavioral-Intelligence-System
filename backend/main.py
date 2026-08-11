from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.database import engine, Base, SessionLocal
from app.services.seed_service import seed_initial_data
from app.api.v1.router import api_router
from app.api.v1.analysis import router as analysis_router
from app.api.v1.users import router as users_router
from app.ml.predictor import predictor_service

# Create DB Tables
Base.metadata.create_all(bind=engine)

# Seed Database if empty
with SessionLocal() as db:
    seed_initial_data(db)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API v1 router (/api/v1)
app.include_router(api_router, prefix=settings.API_V1_STR)

# Direct aliases as requested by user specification (/api/analysis and /api/users)
app.include_router(analysis_router, prefix="/api/analysis", tags=["analysis-direct"])
app.include_router(users_router, prefix="/api/users", tags=["users-direct"])

@app.get("/health")
def health_check():
    model_status = "MODEL LOADED" if predictor_service.is_loaded else "MODEL LOAD ERROR"
    return {
        "status": "healthy",
        "system": settings.PROJECT_NAME,
        "model_status": model_status,
        "features_loaded": len(predictor_service.feature_columns),
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
