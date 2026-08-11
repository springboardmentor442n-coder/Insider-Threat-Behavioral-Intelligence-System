"""
Employee API Routes

Handles:

1. Application Employee CRUD
2. CERT Insider Threat ML Employee Intelligence

IMPORTANT:
Static intelligence routes MUST be declared before
the dynamic /{employee_id} route.
"""

from fastapi import APIRouter, HTTPException, status

from backend.schemas.employee import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeResponse,
    EmployeeIntelligence,
    EmployeeStatistics,
)

from backend.services.employee_service import (
    create_employee_service,
    get_employee,
    get_all_employees_service,
    update_employee_service,
    delete_employee_service,
    get_all_employee_intelligence_service,
    get_employee_intelligence_service,
    get_employee_intelligence_summary_service,
)


router = APIRouter(
    tags=["Employees"],
)


# ============================================================
# ML EMPLOYEE INTELLIGENCE
#
# IMPORTANT:
# These routes MUST appear BEFORE:
#
#     /{employee_id}
#
# Otherwise FastAPI interprets "intelligence" as employee_id.
# ============================================================


@router.get(
    "/intelligence",
    response_model=list[EmployeeIntelligence],
)
def get_employee_intelligence():
    """
    Get behavioral intelligence for all CERT employees.

    Source:
        datasets/exports/employee_final_risk_report.parquet
    """

    try:
        return get_all_employee_intelligence_service()

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )


@router.get(
    "/intelligence/summary",
    response_model=EmployeeStatistics,
)
def get_employee_intelligence_summary():
    """
    Get ML employee risk statistics.
    """

    try:
        return get_employee_intelligence_summary_service()

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )


@router.get(
    "/intelligence/{user}",
    response_model=EmployeeIntelligence,
)
def get_employee_intelligence_by_user(user: str):
    """
    Get ML intelligence for one CERT employee.

    Example:
        /employees/intelligence/AJF0370
    """

    try:
        employee = get_employee_intelligence_service(
            user
        )

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ML employee '{user}' not found.",
        )

    return employee


# ============================================================
# APPLICATION EMPLOYEE CRUD
# ============================================================


@router.post(
    "/",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_employee(employee: EmployeeCreate):
    """
    Create a new application employee.
    """

    created = create_employee_service(
        employee.model_dump()
    )

    if created is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee with this email already exists.",
        )

    return created


@router.get(
    "/",
    response_model=list[EmployeeResponse],
)
def get_all_employees():
    """
    Get all application employees from the database.
    """

    return get_all_employees_service()


# ============================================================
# IMPORTANT:
#
# Dynamic route is intentionally AFTER all static routes.
# ============================================================


@router.get(
    "/{employee_id}",
    response_model=EmployeeResponse,
)
def get_employee_by_id(employee_id: int):
    """
    Get one application employee by database ID.
    """

    employee = get_employee(
        employee_id
    )

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found.",
        )

    return employee


@router.put(
    "/{employee_id}",
    response_model=EmployeeResponse,
)
def update_employee(
    employee_id: int,
    employee: EmployeeUpdate,
):
    """
    Update an application employee.
    """

    updated = update_employee_service(
        employee_id,
        employee.model_dump(
            exclude_unset=True
        ),
    )

    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found.",
        )

    return updated


@router.delete(
    "/{employee_id}",
)
def delete_employee(
    employee_id: int,
):
    """
    Delete an application employee.
    """

    success = delete_employee_service(
        employee_id
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found.",
        )

    return {
        "message": "Employee deleted successfully."
    }
