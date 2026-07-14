from sqlalchemy.orm import Session
from models import User, Employee, Prediction


# -----------------------------
# USER CRUD
# -----------------------------

def create_user(db, username, email, department, password):
    new_user = User(
        username=username,
        email=email,
        department=department,
        password=password,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


def get_users(db: Session):
    return db.query(User).all()


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def update_user(db, user_id, username, email, department, password):
    user = db.query(User).filter(User.id == user_id).first()

    if user:
        user.username = username
        user.email = email
        user.department = department
        user.password = password

        db.commit()
        db.refresh(user)

    return user


def delete_user(db, user_id):
    user = db.query(User).filter(User.id == user_id).first()

    if user:
        db.delete(user)
        db.commit()

    return {"message": "User deleted"}


def login_user(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


# -----------------------------
# EMPLOYEE CRUD
# -----------------------------

def create_employee(
    db,
    employee_id,
    name,
    department,
    designation,
    email,
):
    employee = Employee(
        employee_id=employee_id,
        name=name,
        department=department,
        designation=designation,
        email=email,
    )

    db.add(employee)
    db.commit()
    db.refresh(employee)

    return employee


def get_employees(db: Session):
    return db.query(Employee).all()


def get_employee(db: Session, employee_id: int):
    return (
        db.query(Employee)
        .filter(Employee.id == employee_id)
        .first()
    )
# -----------------------------
# UPDATE / DELETE EMPLOYEE
# -----------------------------

def update_employee(
    db,
    employee_id,
    name,
    department,
    designation,
    email,
):
    employee = (
        db.query(Employee)
        .filter(Employee.id == employee_id)
        .first()
    )

    if employee:
        employee.name = name
        employee.department = department
        employee.designation = designation
        employee.email = email

        db.commit()
        db.refresh(employee)

    return employee


def delete_employee(db, employee_id):
    employee = (
        db.query(Employee)
        .filter(Employee.id == employee_id)
        .first()
    )

    if employee:
        db.delete(employee)
        db.commit()

    return {"message": "Employee deleted"}


# -----------------------------
# PREDICTION CRUD
# -----------------------------

def save_prediction(
    db,
    employee_id,
    login_count,
    unique_pc_count,
    is_weekend,
    hour,
    prediction,
    risk_level,
    confidence,
):
    new_prediction = Prediction(
        employee_id=employee_id,
        login_count=login_count,
        unique_pc_count=unique_pc_count,
        is_weekend=is_weekend,
        hour=hour,
        prediction=prediction,
        risk_level=risk_level,
        confidence=confidence,
    )

    db.add(new_prediction)
    db.commit()
    db.refresh(new_prediction)

    return new_prediction


def get_predictions(db: Session):
    return (
        db.query(Prediction)
        .order_by(Prediction.id.desc())
        .all()
    )


def get_prediction(db: Session, prediction_id: int):
    return (
        db.query(Prediction)
        .filter(Prediction.id == prediction_id)
        .first()
    )
# -----------------------------
# DASHBOARD
# -----------------------------

def get_dashboard_stats(db: Session):
    total_employees = db.query(Employee).count()

    total_predictions = db.query(Prediction).count()

    high_risk = (
        db.query(Prediction)
        .filter(Prediction.risk_level == "HIGH")
        .count()
    )

    low_risk = (
        db.query(Prediction)
        .filter(Prediction.risk_level == "LOW")
        .count()
    )

    return {
        "total_employees": total_employees,
        "total_predictions": total_predictions,
        "high_risk": high_risk,
        "low_risk": low_risk,
    }


# -----------------------------
# DASHBOARD CHART DATA
# -----------------------------

def get_department_statistics(db: Session):
    employees = db.query(Employee).all()

    department_count = {}

    for employee in employees:
        department = employee.department

        if department in department_count:
            department_count[department] += 1
        else:
            department_count[department] = 1

    result = []

    for department, count in department_count.items():
        result.append(
            {
                "department": department,
                "employees": count,
            }
        )

    return result


def get_risk_distribution(db: Session):
    high = (
        db.query(Prediction)
        .filter(Prediction.risk_level == "HIGH")
        .count()
    )

    low = (
        db.query(Prediction)
        .filter(Prediction.risk_level == "LOW")
        .count()
    )

    return [
        {
            "name": "Safe",
            "value": low,
        },
        {
            "name": "Risk",
            "value": high,
        },
    ]