from sqlalchemy.orm import Session
from backend.models import User, Employee, Prediction


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

def save_predictions_bulk(db, predictions):
    db.bulk_save_objects(predictions)
    db.commit()

def get_predictions(db: Session):
    return (
        db.query(Prediction)
        .order_by(Prediction.id.desc())
        .limit(100)
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

# -----------------------------
# BEHAVIOR PROFILE
# -----------------------------

def get_behavior_profiles(db: Session):
    employees = db.query(Employee).all()

    profiles = []

    for employee in employees:

        predictions = (
            db.query(Prediction)
            .filter(Prediction.employee_id == employee.employee_id)
            .all()
        )

        if len(predictions) == 0:

            profiles.append({
                "employee_id": employee.employee_id,
                "name": employee.name,
                "department": employee.department,
                "avg_login": 0,
                "avg_devices": 0,
                "avg_hour": 0,
                "weekend_activity": "No Data",
                "behavior_score": 100,
                "status": "Normal"
            })

            continue

        avg_login = sum(
            p.login_count for p in predictions
        ) / len(predictions)

        avg_devices = sum(
            p.unique_pc_count for p in predictions
        ) / len(predictions)

        avg_hour = sum(
            p.hour for p in predictions
        ) / len(predictions)

        weekend_count = sum(
            p.is_weekend for p in predictions
        )

        high_risk = sum(
            1 for p in predictions
            if p.risk_level == "HIGH"
        )

        score = 100

        score -= high_risk * 20

        if avg_login > 200:
            score -= 10

        if avg_devices > 5:
            score -= 10

        if avg_hour > 20 or avg_hour < 6:
            score -= 10

        score = max(score, 0)

        if score >= 80:
            status = "Normal"
        elif score >= 60:
            status = "Monitor"
        else:
            status = "Suspicious"

        profiles.append({
            "employee_id": employee.employee_id,
            "name": employee.name,
            "department": employee.department,
            "avg_login": round(avg_login, 2),
            "avg_devices": round(avg_devices, 2),
            "avg_hour": round(avg_hour, 2),
            "weekend_activity": weekend_count,
            "behavior_score": score,
            "status": status
        })

    return profiles

from sqlalchemy import func
from backend.models import Employee, Prediction

def get_behavior_profiles(db):
    employees = db.query(Employee).all()

    profiles = []

    for emp in employees:

        predictions = (
            db.query(Prediction)
            .filter(Prediction.employee_id == emp.employee_id)
            .all()
        )

        if len(predictions) == 0:
            profiles.append({
                "employee_id": emp.employee_id,
                "name": emp.name,
                "department": emp.department,
                "avg_login": 0,
                "avg_devices": 0,
                "avg_hour": 0,
                "weekend_activity": "None",
                "behavior_score": 100,
                "status": "Normal"
            })
            continue

        avg_login = round(sum(p.login_count for p in predictions) / len(predictions))
        avg_devices = round(sum(p.unique_pc_count for p in predictions) / len(predictions))
        avg_hour = round(sum(p.hour for p in predictions) / len(predictions))

        weekend_count = sum(p.is_weekend for p in predictions)

        if weekend_count == 0:
            weekend = "Low"
        elif weekend_count < len(predictions) / 2:
            weekend = "Medium"
        else:
            weekend = "High"

        high_risk = sum(1 for p in predictions if p.risk_level == "HIGH")

        score = 100
        score -= high_risk * 10

        if avg_hour >= 22 or avg_hour <= 5:
            score -= 5

        if avg_devices > 4:
            score -= 5

        score = max(score, 0)

        if score >= 80:
            status = "Normal"
        elif score >= 50:
            status = "Monitor"
        else:
            status = "Suspicious"

        profiles.append({
            "employee_id": emp.employee_id,
            "name": emp.name,
            "department": emp.department,
            "avg_login": avg_login,
            "avg_devices": avg_devices,
            "avg_hour": avg_hour,
            "weekend_activity": weekend,
            "behavior_score": score,
            "status": status
        })

    return profiles

from backend.models import Prediction


def save_predictions_bulk(db: Session, predictions):
    """
    Save multiple HIGH-risk predictions to the database
    in a single transaction.
    """

    if not predictions:
        return

    db.bulk_save_objects(predictions)
    db.commit()

def clear_predictions(db: Session):
    db.query(Prediction).delete()
    db.commit()