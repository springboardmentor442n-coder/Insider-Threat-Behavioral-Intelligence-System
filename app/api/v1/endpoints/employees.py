from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.core.security import get_current_user, require_analyst, require_admin
from app.models import Employee, Department, Device, RiskScore, Alert, AlertStatus
from app.schemas import (
    EmployeeCreate, EmployeeUpdate, EmployeeOut, EmployeeDetail,
    DepartmentCreate, DepartmentOut, DeviceCreate, DeviceOut
)

router = APIRouter(prefix="/employees", tags=["Employees"])


# ─── Departments ─────────────────────────────────────────────────────────────
@router.post("/departments", response_model=DepartmentOut, status_code=201)
def create_department(payload: DepartmentCreate, db: Session = Depends(get_db),
                      _=Depends(require_admin)):
    if db.query(Department).filter(Department.code == payload.code).first():
        raise HTTPException(400, "Department code already exists")
    dept = Department(**payload.model_dump())
    db.add(dept); db.commit(); db.refresh(dept)
    return dept


@router.get("/departments", response_model=list[DepartmentOut])
def list_departments(db: Session = Depends(get_db), _=Depends(require_analyst)):
    return db.query(Department).all()


# ─── Employees ────────────────────────────────────────────────────────────────
@router.post("", response_model=EmployeeOut, status_code=201)
def create_employee(payload: EmployeeCreate, db: Session = Depends(get_db),
                    _=Depends(require_analyst)):
    if db.query(Employee).filter(Employee.employee_id == payload.employee_id).first():
        raise HTTPException(400, "Employee ID already exists")
    if db.query(Employee).filter(Employee.email == payload.email).first():
        raise HTTPException(400, "Email already exists")
    emp = Employee(**payload.model_dump())
    db.add(emp); db.commit(); db.refresh(emp)
    return emp


@router.get("", response_model=list[EmployeeOut])
def list_employees(
    db: Session = Depends(get_db),
    _=Depends(require_analyst),
    department_id: Optional[int] = Query(None),
    is_active: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    risk_category: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    q = db.query(Employee)
    if department_id:
        q = q.filter(Employee.department_id == department_id)
    if is_active is not None:
        q = q.filter(Employee.is_active == is_active)
    if search:
        q = q.filter(
            Employee.full_name.ilike(f"%{search}%") |
            Employee.employee_id.ilike(f"%{search}%") |
            Employee.email.ilike(f"%{search}%")
        )
    return q.offset((page - 1) * page_size).limit(page_size).all()


@router.get("/{employee_id}", response_model=EmployeeDetail)
def get_employee(employee_id: int, db: Session = Depends(get_db),
                 _=Depends(require_analyst)):
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(404, "Employee not found")

    # Enrich with latest risk score
    latest_risk = (db.query(RiskScore)
                   .filter(RiskScore.employee_id == employee_id)
                   .order_by(RiskScore.score_date.desc())
                   .first())
    open_alerts = (db.query(func.count(Alert.id))
                   .filter(Alert.employee_id == employee_id,
                           Alert.status == AlertStatus.open)
                   .scalar())

    result = EmployeeDetail.model_validate(emp)
    if latest_risk:
        result.current_risk_score = latest_risk.total_score
        result.current_risk_category = latest_risk.risk_category
    result.open_alerts_count = open_alerts or 0
    return result


@router.put("/{employee_id}", response_model=EmployeeOut)
def update_employee(employee_id: int, payload: EmployeeUpdate,
                    db: Session = Depends(get_db), _=Depends(require_analyst)):
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(404, "Employee not found")
    for k, v in payload.model_dump(exclude_none=True).items():
        setattr(emp, k, v)
    db.commit(); db.refresh(emp)
    return emp


@router.delete("/{employee_id}", status_code=204)
def terminate_employee(employee_id: int, db: Session = Depends(get_db),
                       _=Depends(require_admin)):
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(404, "Employee not found")
    from datetime import datetime, timezone
    emp.is_terminated = True
    emp.is_active = False
    emp.termination_date = datetime.now(timezone.utc)
    db.commit()


# ─── Devices ─────────────────────────────────────────────────────────────────
@router.post("/{employee_id}/devices", response_model=DeviceOut, status_code=201)
def add_device(employee_id: int, payload: DeviceCreate, db: Session = Depends(get_db),
               _=Depends(require_analyst)):
    if not db.query(Employee).filter(Employee.id == employee_id).first():
        raise HTTPException(404, "Employee not found")
    device = Device(**payload.model_dump())
    db.add(device); db.commit(); db.refresh(device)
    return device


@router.get("/{employee_id}/devices", response_model=list[DeviceOut])
def list_devices(employee_id: int, db: Session = Depends(get_db),
                 _=Depends(require_analyst)):
    return db.query(Device).filter(Device.employee_id == employee_id).all()
