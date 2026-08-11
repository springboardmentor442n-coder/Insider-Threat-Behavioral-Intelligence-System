"""
Employee Repository

Database operations for Employee model.
"""

from typing import Optional

from sqlalchemy.orm import Session

from backend.database.models import Employee


def create_employee(
    db: Session,
    employee_data: dict,
) -> Employee:
    """
    Create a new employee.
    """

    employee = Employee(**employee_data)

    db.add(employee)
    db.commit()
    db.refresh(employee)

    return employee


def get_employee_by_id(
    db: Session,
    employee_id: int,
) -> Optional[Employee]:
    """
    Fetch employee by ID.
    """

    return (
        db.query(Employee)
        .filter(Employee.id == employee_id)
        .first()
    )


def get_employee_by_email(
    db: Session,
    email: str,
) -> Optional[Employee]:
    """
    Fetch employee by email.
    """

    return (
        db.query(Employee)
        .filter(Employee.email == email)
        .first()
    )


def get_all_employees(
    db: Session,
):
    """
    Return all employees.
    """

    return (
        db.query(Employee)
        .order_by(Employee.id)
        .all()
    )


def update_employee(
    db: Session,
    employee: Employee,
    updates: dict,
) -> Employee:
    """
    Update an employee.
    """

    for key, value in updates.items():
        setattr(employee, key, value)

    db.commit()
    db.refresh(employee)

    return employee


def delete_employee(
    db: Session,
    employee: Employee,
):
    """
    Delete employee.
    """

    db.delete(employee)
    db.commit()

    return True
