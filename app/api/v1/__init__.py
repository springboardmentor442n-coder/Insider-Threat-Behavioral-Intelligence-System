from fastapi import APIRouter
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.employees import router as employee_router
from app.api.v1.endpoints.activities import router as activity_router
from app.api.v1.endpoints.security import (
    anomaly_router, risk_router, alert_router,
    incident_router, dashboard_router,
)
from app.api.v1.endpoints.ml_endpoints import router as ml_router
from app.api.v1.endpoints.reports import router as reports_router
from app.api.v1.endpoints.chatbot import router as chatbot_router
from app.api.v1.endpoints.simulation import router as simulation_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(employee_router)
api_router.include_router(activity_router)
api_router.include_router(anomaly_router)
api_router.include_router(risk_router)
api_router.include_router(alert_router)
api_router.include_router(incident_router)
api_router.include_router(dashboard_router)
api_router.include_router(ml_router)
api_router.include_router(reports_router)
api_router.include_router(chatbot_router)
api_router.include_router(simulation_router)
