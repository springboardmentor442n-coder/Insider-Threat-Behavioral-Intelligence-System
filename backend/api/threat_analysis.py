"""
===============================================================================
API Router    : Live Individual Employee Threat Analysis API
File          : backend/api/threat_analysis.py
Project       : Insider Threat Behavioral Intelligence System / SentinelAI

Endpoints     :
    POST /threat-analysis/analyze
===============================================================================
"""

from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any

from backend.services.live_threat_analyzer_service import analyze_live_employee_threat
from backend.services.verification_service import add_custom_employee_to_system

router = APIRouter(
    prefix="/threat-analysis",
    tags=["Threat Analysis"],
)


@router.post(
    "/analyze",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Analyze Custom Employee Live Behavioral Feature Vector",
    description="Evaluates custom feature inputs through pre-trained 7-model ML pipeline and CERT Layer 2 verification.",
)
def analyze_custom_threat(payload: Dict[str, Any]):
    """
    Live threat analysis for an individual employee feature vector.
    """
    try:
        emp_id = str(payload.get("employee_id") or payload.get("user") or "CUSTOM-001").strip().upper()
        emp_name = payload.get("employee_name") or payload.get("name")
        department = payload.get("department")
        role = payload.get("role")

        raw_features = payload.get("features")
        if raw_features is None:
            # If features passed at root level
            raw_features = payload

        result = analyze_live_employee_threat(
            employee_id=emp_id,
            raw_features=raw_features,
            employee_name=emp_name,
            department=department,
            role=role,
        )
        return result
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err),
        )
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing live employee threat: {str(err)}",
        )
