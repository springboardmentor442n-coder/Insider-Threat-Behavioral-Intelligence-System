from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.models import User, Employee, Prediction, BehaviorFeature, PipelineRun, Alert


# -----------------------------
# USER CRUD
# -----------------------------

def create_user(db: Session, username, email, department, password):
    user = User(
        username=username,
        email=email,
        department=department,
        password=password
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def get_users(db: Session):
    return db.query(User).all()


def get_user(db: Session, user_id: int):
    return (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )


def update_user(
    db: Session,
    user_id,
    username,
    email,
    department,
    password
):

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        return None

    user.username = username
    user.email = email
    user.department = department
    user.password = password

    db.commit()
    db.refresh(user)

    return user


def delete_user(db: Session, user_id):

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        return None

    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully"}


def login_user(db: Session, username: str):

    return (
        db.query(User)
        .filter(User.username == username)
        .first()
    )
# -----------------------------
# EMPLOYEE CRUD
# -----------------------------

def create_employee(
    db: Session,
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

    return (
        db.query(Employee)
        .order_by(Employee.id)
        .all()
    )


def get_employee(db: Session, employee_id: int):

    return (
        db.query(Employee)
        .filter(Employee.id == employee_id)
        .first()
    )


def update_employee(
    db: Session,
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

    if not employee:
        return None

    employee.name = name
    employee.department = department
    employee.designation = designation
    employee.email = email

    db.commit()
    db.refresh(employee)

    return employee


def delete_employee(db: Session, employee_id):

    employee = (
        db.query(Employee)
        .filter(Employee.id == employee_id)
        .first()
    )

    if not employee:
        return None

    db.delete(employee)
    db.commit()

    return {"message": "Employee deleted successfully"}


# -----------------------------
# PREDICTION CRUD
# -----------------------------

def save_prediction(
    db: Session,
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


def save_predictions_bulk(db: Session, predictions):
    """
    Save multiple predictions in one transaction.
    """

    if not predictions:
        return

    db.bulk_save_objects(predictions)
    db.commit()


def clear_predictions(db: Session):
    """
    Remove all prediction records.
    Used before importing a fresh CERT dataset.
    """

    db.query(Prediction).delete()
    db.commit()


def get_predictions(db: Session):

    predictions = (
        db.query(Prediction)
        .order_by(Prediction.id.desc())
        .limit(1000)
        .all()
    )

    results = []

    for prediction in predictions:

        employee = (
            db.query(Employee)
            .filter(
                Employee.employee_id == prediction.employee_id
            )
            .first()
        )

        results.append({

            "prediction_id": prediction.id,

            "employee_id": prediction.employee_id,

            "employee_name":
                employee.name if employee else prediction.employee_id,

            "department":
                employee.department if employee else "Unknown",

            "designation":
                employee.designation if employee else "Employee",

            "login_count":
                prediction.login_count,

            "unique_pc_count":
                prediction.unique_pc_count,

            "hour":
                prediction.hour,

            "is_weekend":
                prediction.is_weekend,

            "prediction":
                prediction.prediction,

            "risk_level":
                prediction.risk_level,

            "confidence":
                round(prediction.confidence, 2)

        })

    return results


def get_prediction(
    db: Session,
    prediction_id: int
):

    return (
        db.query(Prediction)
        .filter(Prediction.id == prediction_id)
        .first()
    )
# -----------------------------
# DASHBOARD STATISTICS
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

    average_confidence = (
        db.query(func.avg(Prediction.confidence))
        .scalar()
    )

    average_confidence = round(
        average_confidence or 0,
        2
    )

    recent_alerts = (
        db.query(Prediction)
        .filter(Prediction.risk_level == "HIGH")
        .order_by(Prediction.id.desc())
        .limit(10)
        .count()
    )

    return {

        "total_employees": total_employees,

        "total_predictions": total_predictions,

        "high_risk": high_risk,

        "low_risk": low_risk,

        "average_confidence": average_confidence,

        "recent_alerts": recent_alerts

    }

# -----------------------------
# DASHBOARD CHARTS
# -----------------------------

def get_department_statistics(db: Session):

    departments = (
        db.query(
            Employee.department,
            func.count(Employee.id)
        )
        .group_by(Employee.department)
        .all()
    )

    return [

        {
            "department": dept,
            "employees": count
        }

        for dept, count in departments

    ]


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
            "name": "High Risk",
            "value": high
        },

        {
            "name": "Low Risk",
            "value": low
        }

    ]

def get_login_hour_distribution(db: Session):

    hours = []

    for hour in range(24):

        count = (
            db.query(BehaviorFeature)
            .filter(
                func.floor(
                    BehaviorFeature.average_login_hour
                ) == hour
            )
            .count()
        )

        hours.append(
            {
                "hour": hour,
                "count": count
            }
        )

    return hours

# -----------------------------
# BEHAVIOR PROFILE
# -----------------------------

def get_behavior_profiles(db: Session):

    employees = db.query(Employee).all()

    profiles = []

    for employee in employees:

        behavior = (
            db.query(BehaviorFeature)
            .filter(
                BehaviorFeature.employee_id == employee.employee_id
            )
            .first()
        )

        prediction = (
            db.query(Prediction)
            .filter(
                Prediction.employee_id == employee.employee_id
            )
            .order_by(Prediction.id.desc())
            .first()
        )

        if not behavior:

            profiles.append({
                "employee_id": employee.employee_id,
                "name": employee.name,
                "department": employee.department,
                "designation": employee.designation,
                "avg_login": 0,
                "avg_devices": 0,
                "avg_hour": 0,
                "weekend_activity": 0,
                "risk_score": 0,
                "behavior_score": 100,
                "status": "No Activity"
            })

            continue

        if prediction:
            status = prediction.risk_level

            if prediction.risk_level == "HIGH":
                risk_score = round(prediction.confidence, 2)
            else:
                risk_score = round((1 - prediction.confidence), 2)

        else:
            risk_score = 0
            status = "No Prediction"

        profiles.append({

            "employee_id": employee.employee_id,

            "name": employee.name,

            "department": employee.department,

            "designation": employee.designation,

            "avg_login": behavior.login_count,

            "avg_devices": behavior.unique_pc_count,

            "avg_hour": round(
                behavior.average_login_hour,
                2
            ) if behavior.average_login_hour else 0,

            "weekend_activity": behavior.weekend_logins,

            "risk_score": risk_score,

            "behavior_score": round(
                100 - risk_score,
                2
            ),

            "status": status

        })

    profiles.sort(
        key=lambda x: x["risk_score"],
        reverse=True
    )

    return profiles

# -----------------------------
# TOP HIGH RISK EMPLOYEES
# -----------------------------

def get_top_risk_employees(db: Session, limit: int = 10):

    profiles = get_behavior_profiles(db)

    return profiles[:limit]


# -----------------------------
# RECENT THREAT ALERTS
# -----------------------------

def get_recent_alerts(db: Session, limit: int = 10):

    predictions = (
        db.query(Prediction)
        .filter(Prediction.risk_level == "HIGH")
        .order_by(Prediction.id.desc())
        .limit(limit)
        .all()
    )

    alerts = []

    for prediction in predictions:

        employee = (
            db.query(Employee)
            .filter(
                Employee.employee_id ==
                prediction.employee_id
            )
            .first()
        )

        alerts.append({

            "employee_id": prediction.employee_id,

            "employee_name":
                employee.name if employee
                else prediction.employee_id,

            "department":
                employee.department if employee
                else "Unknown",

            "risk_level":
                prediction.risk_level,

            "confidence":
                prediction.confidence,

            "hour":
                prediction.hour

        })

    return alerts


# -----------------------------
# EMPLOYEE DETAILS
# -----------------------------

def get_employee_profile(
    db: Session,
    employee_id: str
):

    employee = (
        db.query(Employee)
        .filter(Employee.employee_id == employee_id)
        .first()
    )

    if employee is None:
        return None

    predictions = (
        db.query(Prediction)
        .filter(Prediction.employee_id == employee_id)
        .order_by(Prediction.id.desc())
        .all()
    )

    employee_data = {
        "employee_id": employee.employee_id,
        "name": employee.name,
        "department": employee.department,
        "designation": employee.designation,
        "email": employee.email,
    }

    prediction_data = []

    for p in predictions:

        prediction_data.append({

            "id": p.id,

            "login_count": p.login_count,

            "unique_pc_count": p.unique_pc_count,

            "hour": p.hour,

            "is_weekend": p.is_weekend,

            "prediction": p.prediction,

            "risk_level": p.risk_level,

            "confidence": p.confidence,

        })

    return {

        "employee": employee_data,

        "predictions": prediction_data,

        "total_predictions": len(predictions),

        "high_risk": sum(
            1
            for p in predictions
            if p.risk_level == "HIGH"
        )

    }

# -----------------------------
# TOP HIGH RISK EMPLOYEES
# -----------------------------

def get_behavior_features(db: Session):
    return (
        db.query(BehaviorFeature)
        .order_by(BehaviorFeature.employee_id)
        .all()
    )