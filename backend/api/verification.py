"""
===============================================================================
API Router    : CERT Behavioral Pattern Validation API Router
File          : backend/api/verification.py
Project       : Insider Threat Behavioral Intelligence System

Endpoints     :
    GET /verification/behavioral-summary
    GET /verification/employee/{user_id}

Description   :
    Exposes endpoints for CERT Behavioral Pattern Validation (Layer 2).
    Evaluates ML-detected suspicious users against population-level baselines
    across CERT-documented anomaly vectors (Temporal, USB/Device, Multi-PC,
    Web, Email, Overall Volume).
===============================================================================
"""

from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any

from backend.services.verification_service import (
    get_behavioral_validation_summary,
    get_individual_employee_behavioral_validation,
    DISCLAIMER_TEXT,
)

router = APIRouter(
    prefix="/verification",
    tags=["Verification"],
)


@router.get(
    "/behavioral-summary",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Get Population Behavioral Pattern Validation Summary",
    description=(
        "Returns population-wide behavioral validation metrics comparing "
        "ML-detected suspicious users against CERT R4.2 behavioral anomaly vectors."
    ),
)
def get_behavioral_summary():
    """
    Returns population summary for CERT Behavioral Pattern Validation.
    """
    try:
        summary = get_behavioral_validation_summary()
        return summary
    except FileNotFoundError as fnf_err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(fnf_err),
        )
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating behavioral validation summary: {str(err)}",
        )


@router.get(
    "/employee/{user_id}",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Get Individual Employee CERT Behavioral Evidence",
    description=(
        "Returns detailed CERT behavioral vector evaluation and population-baseline "
        "evidence for a specific employee ID."
    ),
)
def get_employee_behavioral_evidence(user_id: str):
    """
    Returns individual employee behavioral validation evidence.
    """
    try:
        result = get_individual_employee_behavioral_validation(user_id)
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Employee '{user_id}' not found in behavioral intelligence dataset.",
            )
        return result
    except HTTPException:
        raise
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error evaluating employee behavioral validation for '{user_id}': {str(err)}",
        )
