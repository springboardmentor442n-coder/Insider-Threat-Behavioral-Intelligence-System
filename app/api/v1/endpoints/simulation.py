"""
Real-Time Simulation API Endpoints
==================================
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.core.security import require_analyst
from app.services import simulation

router = APIRouter(prefix="/simulation", tags=["Simulation Control"])


class TogglePayload(BaseModel):
    active: bool


@router.post("/toggle")
def toggle_simulation(payload: TogglePayload, _=Depends(require_analyst)):
    """
    Toggle real-time enterprise simulation.
    Requires analyst credentials.
    """
    active = simulation.toggle_demo_mode(payload.active)
    return {"status": "success", "demo_mode_active": active}


@router.get("/status")
def get_simulation_status():
    """
    Get current simulation status.
    """
    return {"demo_mode_active": simulation.get_demo_mode_status()}
