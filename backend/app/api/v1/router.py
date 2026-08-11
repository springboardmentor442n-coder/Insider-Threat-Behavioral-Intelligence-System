from fastapi import APIRouter
from app.api.v1 import auth, dashboard, users, analytics, prediction, alerts, investigations, reports, analysis, explainability

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(prediction.router, prefix="/predict", tags=["prediction"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
api_router.include_router(explainability.router, prefix="/explainability", tags=["explainability"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(investigations.router, prefix="/investigations", tags=["investigations"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
