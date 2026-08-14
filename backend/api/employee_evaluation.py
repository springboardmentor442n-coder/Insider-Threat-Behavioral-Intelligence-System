"""
===============================================================================
API Router    : New Employee Evaluation API
File          : backend/api/employee_evaluation.py
Project       : Insider Threat Behavioral Intelligence System / SentinelAI

Endpoints     :
    POST   /employee-evaluation/evaluate
    POST   /employee-evaluation/save
    GET    /employee-evaluation/
    GET    /employee-evaluation/{employee_id}
    DELETE /employee-evaluation/{employee_id}        [Administrator only]
    GET    /employee-evaluation/comparison/summary
    GET    /employee-evaluation/comparison/ranking
    GET    /employee-evaluation/comparison/{employee_id}

RBAC          :
    Security Analyst    : evaluate, view, compare
    SOC Engineer        : evaluate, view, compare
    Security Manager    : view, compare
    Administrator       : full access including delete
===============================================================================
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Any, Dict, List

from backend.utils.security import get_current_user
from backend.utils.roles import require_roles

from backend.services.employee_evaluation_service import (
    evaluate_employee,
    save_evaluation,
    evaluate_and_store,
    get_all_evaluations,
    get_evaluation,
    delete_evaluation,
    get_comparison_summary,
    get_comparison_ranking,
    get_individual_comparison,
)

router = APIRouter(
    prefix="/employee-evaluation",
    tags=["Employee Evaluation"],
)


# =============================================================================
# Evaluate (inference only — does NOT save)
# =============================================================================

@router.post(
    "/evaluate",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Evaluate New Employee Behavioral Feature Vector",
    description=(
        "Runs the 22-feature vector through the existing pre-trained 7-model ML pipeline "
        "and CERT Layer 2 behavioral verification. Result is returned for review. "
        "Use /save to persist the result to the session store."
    ),
)
def evaluate(
    payload: Dict[str, Any],
    current_user=Depends(require_roles(
        "Security Analyst", "SOC Engineer", "Administrator", "analyst", "soc", "admin"
    )),
):
    try:
        emp_id = str(
            payload.get("employee_id") or payload.get("user") or "NEW-001"
        ).strip().upper()
        emp_name = payload.get("employee_name") or payload.get("name")
        department = payload.get("department")
        role = payload.get("role")
        raw_features = payload.get("features") or payload

        result = evaluate_employee(
            employee_id=emp_id,
            raw_features=raw_features,
            employee_name=emp_name,
            department=department,
            role=role,
        )
        return result
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Evaluation error: {str(err)}",
        )


# =============================================================================
# Save
# =============================================================================

@router.post(
    "/save",
    response_model=Dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    summary="Save Evaluated Employee to Session Store",
    description=(
        "Persists a completed evaluation result to the in-memory session evaluation store "
        "with source='NEW_EVALUATION'. The CERT R4.2 dataset is NOT modified."
    ),
)
def save(
    payload: Dict[str, Any],
    current_user=Depends(require_roles(
        "Security Analyst", "SOC Engineer", "Administrator", "analyst", "soc", "admin"
    )),
):
    try:
        record = save_evaluation(payload)
        return record
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Save error: {str(err)}",
        )


# =============================================================================
# List all evaluations
# =============================================================================

@router.get(
    "/",
    response_model=List[Dict[str, Any]],
    status_code=status.HTTP_200_OK,
    summary="List All Newly Evaluated Employees",
    description="Returns all employees in the session evaluation store (source='NEW_EVALUATION'), sorted by risk score descending.",
)
def list_evaluations(
    current_user=Depends(get_current_user),
):
    try:
        return get_all_evaluations()
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving evaluations: {str(err)}",
        )


# =============================================================================
# Get single evaluation — must be BEFORE /{employee_id} to avoid route conflicts
# =============================================================================

@router.get(
    "/comparison/summary",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="CERT vs New Evaluation Comparison Summary",
    description=(
        "Aggregates risk statistics for the CERT R4.2 population and the session "
        "evaluation store. The CERT baseline is never modified."
    ),
)
def comparison_summary(
    current_user=Depends(get_current_user),
):
    try:
        return get_comparison_summary()
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error computing comparison summary: {str(err)}",
        )


@router.get(
    "/comparison/ranking",
    response_model=List[Dict[str, Any]],
    status_code=status.HTTP_200_OK,
    summary="Combined CERT + New Evaluation Risk Ranking",
    description=(
        "Returns a combined risk ranking: Top 50 CERT employees by risk score "
        "plus ALL newly evaluated employees, merged and ranked by risk score. "
        "Each record includes an explicit 'source' field: CERT_R4.2 or NEW_EVALUATION."
    ),
)
def comparison_ranking(
    current_user=Depends(get_current_user),
):
    try:
        return get_comparison_ranking()
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error computing comparison ranking: {str(err)}",
        )


@router.get(
    "/comparison/{employee_id}",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Individual Employee Percentile Comparison vs CERT Population",
    description=(
        "For a single NEW_EVALUATION employee, returns their percentile rank within the "
        "CERT R4.2 population across all 6 behavioral dimensions and the overall risk score. "
        "The employee is NOT added to the CERT baseline."
    ),
)
def individual_comparison(
    employee_id: str,
    current_user=Depends(get_current_user),
):
    try:
        return get_individual_comparison(employee_id)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error computing individual comparison: {str(err)}",
        )


# =============================================================================
# Get one evaluation
# =============================================================================

@router.get(
    "/{employee_id}",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Get One Evaluation Detail",
)
def get_one(
    employee_id: str,
    current_user=Depends(get_current_user),
):
    try:
        record = get_evaluation(employee_id)
        if record is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No evaluation found for employee_id='{employee_id}'",
            )
        return record
    except HTTPException:
        raise
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving evaluation: {str(err)}",
        )


# =============================================================================
# Delete (Administrator only)
# =============================================================================

@router.delete(
    "/{employee_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete Evaluation Record (Administrator Only)",
)
def delete(
    employee_id: str,
    current_user=Depends(require_roles("Administrator", "admin")),
):
    try:
        deleted = delete_evaluation(employee_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No evaluation found for employee_id='{employee_id}'",
            )
        return {
            "message": f"Evaluation for '{employee_id}' deleted successfully.",
            "employee_id": employee_id.strip().upper(),
        }
    except HTTPException:
        raise
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Delete error: {str(err)}",
        )
