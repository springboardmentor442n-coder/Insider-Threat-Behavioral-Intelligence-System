from backend.security import hash_password, verify_password, create_access_token
from fastapi import HTTPException
from sqlalchemy.orm import Session
from database.models import User, Prediction, Employee

def create_user(db: Session,username: str,email: str,department: str,password: str):

    existing_user = db.query(User).filter(
        (User.username == username) | (User.email == email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username or email already exists"
        )
    print("Password:", password)
    print("Type:", type(password))
    user = User(
        username=username,
        email=email,
        department=department,
        password=hash_password(password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user

def get_users(db: Session):
    return db.query(User).all()

def get_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user

def update_user(db: Session, user_id: int, username: str, email: str, department: str):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.username = username
    user.email = email
    user.department = department

    db.commit()
    db.refresh(user)

    return user

def delete_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully"}

def login_user(db: Session, username: str, password: str):

    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token(
        {"sub": user.username}
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }

def save_prediction(
    db,
    login_count,
    unique_pc_count,
    is_weekend,
    hour,
    prediction,
    risk_level,
    confidence
):
    new_prediction = Prediction(
        login_count=login_count,
        unique_pc_count=unique_pc_count,
        is_weekend=is_weekend,
        hour=hour,
        prediction=prediction,
        risk_level=risk_level,
        confidence=confidence
    )

    db.add(new_prediction)
    db.commit()
    db.refresh(new_prediction)

    return new_prediction

def create_employee(
    db: Session,
    employee_id: str,
    name: str,
    department: str,
    designation: str,
    email: str
):
    employee = Employee(
        employee_id=employee_id,
        name=name,
        department=department,
        designation=designation,
        email=email
    )

    db.add(employee)
    db.commit()
    db.refresh(employee)

    return employee


def get_employees(db: Session):
    return db.query(Employee).all()


def get_employee(db: Session, employee_id: int):
    return db.query(Employee).filter(Employee.id == employee_id).first()


def update_employee(
    db: Session,
    employee_id: int,
    name: str,
    department: str,
    designation: str,
    email: str
):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()

    if not employee:
        return None

    employee.name = name
    employee.department = department
    employee.designation = designation
    employee.email = email

    db.commit()
    db.refresh(employee)

    return employee


def delete_employee(db: Session, employee_id: int):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()

    if not employee:
        return None

    db.delete(employee)
    db.commit()

    return employee