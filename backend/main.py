from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import engine, Base

from backend.routes import auth
from backend.routes import upload
from backend.routes import pipeline

from backend.routes.employee import router as employee_router
from backend.routes.dashboard import router as dashboard_router
from backend.routes.behavior import router as behavior_router
from backend.routes.prediction import router as prediction_router
from backend.routes import behavior
# Create Database Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Insider Threat Behavioral Intelligence System"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(employee_router)
app.include_router(prediction_router)
app.include_router(dashboard_router)
app.include_router(behavior_router)
app.include_router(upload.router)
app.include_router(pipeline.router)
app.include_router(behavior.router)

@app.get("/")
def home():
    try:
        connection = engine.connect()
        connection.close()

        return {
            "message": "Hello Sristi! Backend is running.",
            "database": "Connected successfully!"
        }

    except Exception as e:
        return {
            "message": "Backend is running.",
            "database": str(e)
        }