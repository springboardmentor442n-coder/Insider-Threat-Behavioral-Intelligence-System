"""
Employee API Routes
"""

from fastapi import APIRouter, HTTPException, status

from backend.schemas.employee import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeResponse,
)

from backend.services.employee_service import (
    create_employee_service,
    get_employee,
    get_all_employees_service,
    update_employee_service,
    delete_employee_service,
)

router = APIRouter(
    tags=["Employees"],
)

@router.post(
    "/",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_employee(employee: EmployeeCreate):
    """
    Create a new employee.
    """

    created = create_employee_service(employee.model_dump())

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
    Get all employees.
    """

    return get_all_employees_service()


@router.get(
    "/{employee_id}",
    response_model=EmployeeResponse,
)
def get_employee_by_id(employee_id: int):
    """
    Get employee by ID.
    """

    employee = get_employee(employee_id)

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
    Update employee.
    """

    updated = update_employee_service(
        employee_id,
        employee.model_dump(exclude_unset=True),
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
def delete_employee(employee_id: int):
    """
    Delete employee.
    """

    success = delete_employee_service(employee_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found.",
        )

    return {
        "message": "Employee deleted successfully."
    }
