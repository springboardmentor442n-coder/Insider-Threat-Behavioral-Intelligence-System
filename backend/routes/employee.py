from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.config import get_db
from backend.crud import (
    create_employee,
    get_employees,
    get_employee,
    update_employee,
    delete_employee,
)

from backend.schemas import EmployeeCreate

router = APIRouter()

@router.post("/employees")
def add_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):
    return create_employee(
        db,
        employee.employee_id,
        employee.name,
        employee.department,
        employee.designation,
        employee.email,
    )


@router.get("/employees")
def read_employees(db: Session = Depends(get_db)):
    return get_employees(db)


@router.get("/employees/{employee_id}")
def read_employee(employee_id: int, db: Session = Depends(get_db)):
    return get_employee(db, employee_id)


@router.put("/employees/{employee_id}")
def edit_employee(employee_id: int, employee: EmployeeCreate, db: Session = Depends(get_db)):
    return update_employee(
        db,
        employee_id,
        employee.name,
        employee.department,
        employee.designation,
        employee.email,
    )


@router.delete("/employees/{employee_id}")
def remove_employee(employee_id: int, db: Session = Depends(get_db)):
    return delete_employee(db, employee_id)