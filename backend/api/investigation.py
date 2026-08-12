from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Depends

from backend.utils.roles import require_roles
from backend.utils.security import get_current_user

from backend.services.investigation_service import (
    get_all_cases,
    get_case,
    create_or_get_investigation,
    update_case_status,
    assign_case,
    add_note,
    escalate_case,
)

router = APIRouter(
    prefix="/investigation",
    tags=["Investigation"],
)


@router.get("")
def investigations(
    current_user=Depends(
        require_roles(
            "admin",
            "analyst",
        )
    ),
):
    return get_all_cases()


@router.post("/create/{employee_id}")
def create_investigation(
    employee_id: str,
    current_user=Depends(
        require_roles(
            "admin",
            "analyst",
        )
    ),
):
    return create_or_get_investigation(employee_id)


@router.get("/{case_id}")
def investigation(
    case_id: str,
    current_user=Depends(
        require_roles(
            "admin",
            "analyst",
        )
    ),
):
    case = get_case(case_id)

    if not case:
        raise HTTPException(404, "Case not found")

    return case


@router.post("/{case_id}/status")
def status(
    case_id: str,
    status: str,
    current_user=Depends(
        require_roles(
            "admin",
            "analyst",
        )
    ),
):
    case = update_case_status(case_id, status)

    if not case:
        raise HTTPException(404, "Case not found")

    return case


@router.post("/{case_id}/assign")
def assign(
    case_id: str,
    analyst: str,
    current_user=Depends(
        require_roles(
            "admin",
            "analyst",
        )
    ),
):
    case = assign_case(case_id, analyst)

    if not case:
        raise HTTPException(404, "Case not found")

    return case


@router.post("/{case_id}/notes")
def notes(
    case_id: str,
    note: str,
    current_user=Depends(
        require_roles(
            "admin",
            "analyst",
        )
    ),
):
    case = add_note(case_id, note)

    if not case:
        raise HTTPException(404, "Case not found")

    return case


@router.post("/{case_id}/escalate")
def escalate(
    case_id: str,
    current_user=Depends(get_current_user),
):
    case = escalate_case(case_id, username=current_user.username)

    if not case:
        raise HTTPException(404, "Case not found")

    return case
    