from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.models import (
    User,
    Employee,
    Prediction,
    BehaviorFeature,
    PipelineRun,
    Alert,
)

# ============================================================
# USER CRUD
# ============================================================

def create_user(db: Session, username, email, department, password):
    user = User(
        username=username,
        email=email,
        department=department,
        password=password,
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
    password,
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


# ============================================================
# EMPLOYEE CRUD
# ============================================================

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
# ============================================================
# PREDICTION CRUD
# ============================================================

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
    """
    db.query(Prediction).delete()
    db.commit()


def get_predictions(db: Session):

    predictions = (
    db.query(Prediction)
    .order_by(Prediction.event_timestamp.desc())
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
                employee.name if employee
                else prediction.employee_id,

            "department":
                employee.department if employee
                else "Unknown",

            "designation":
                employee.designation if employee
                else "Employee",

            "login_count":
                prediction.login_count,

            "unique_pc_count":
                prediction.unique_pc_count,

           "timestamp": (
    prediction.event_timestamp.strftime("%d %b %Y %I:%M %p")
    if prediction.event_timestamp
    else "-"
),

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


# ============================================================
# DASHBOARD STATISTICS
# ============================================================

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


# ============================================================
# DASHBOARD CHARTS
# ============================================================

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

        hours.append({

            "hour": hour,

            "count": count

        })

    return hours
# ============================================================
# BEHAVIOR PROFILE
# ============================================================

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
            .order_by(
                Prediction.event_timestamp.desc()
            )
            .first()
        )

        # Skip employees without behaviour data
        if behavior is None:
            continue

        if prediction:

            status = prediction.risk_level

            if prediction.risk_level == "HIGH":
                risk_score = round(prediction.confidence, 2)
            else:
                risk_score = round(
                    (1 - prediction.confidence) * 100,
                    2
                )

            confidence = round(
                prediction.confidence,
                2
            )

            last_prediction = (
                prediction.event_timestamp.strftime(
                    "%d %b %Y %I:%M %p"
                )
                if prediction.event_timestamp
                else "-"
            )

        else:

            status = "No Prediction"

            risk_score = 0

            confidence = 0

            last_prediction = "-"

        profiles.append({

            "employee_id": employee.employee_id,

            "employee_name": employee.name,

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

            "confidence": confidence,

            "last_prediction": last_prediction,

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


# ============================================================
# TOP HIGH RISK EMPLOYEES
# ============================================================

def get_top_risk_employees(
    db: Session,
    limit: int = 10
):

    profiles = get_behavior_profiles(db)

    return profiles[:limit]


# ============================================================
# RECENT THREAT ALERTS
# ============================================================

def get_recent_alerts(
    db: Session,
    limit: int = 10
):

    predictions = (
        db.query(Prediction)
        .filter(
    Prediction.risk_level == "HIGH"
)
.order_by(
    Prediction.event_timestamp.desc()
)
.limit(limit)
.all())

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

            "employee_id":
                prediction.employee_id,

            "employee_name":
                employee.name
                if employee
                else prediction.employee_id,

            "department":
                employee.department
                if employee
                else "Unknown",

            "risk_level":
                prediction.risk_level,

            "confidence":
                round(
                    prediction.confidence,
                    2
                ),

            "timestamp":
    prediction.event_timestamp.strftime("%d %b %Y %I:%M %p")
    if prediction.event_timestamp
    else "-",

            "alert_type":
                "High Risk Employee"

        })

    return alerts
# ============================================================
# EMPLOYEE DETAILS
# ============================================================

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
    .filter(
        Prediction.employee_id == employee_id
    )
    .order_by(
        Prediction.event_timestamp.desc()
    )
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

            "confidence": round(p.confidence, 2),

            "timestamp": (
    p.event_timestamp.strftime("%d %b %Y %I:%M %p")
    if p.event_timestamp
    else "-"
)

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


# ============================================================
# BEHAVIOR FEATURES
# ============================================================

def get_behavior_features(db: Session):

    return (

        db.query(BehaviorFeature)

        .order_by(
            BehaviorFeature.employee_id
        )

        .all()

    )


def save_behavior_features(
    db: Session,
    feature_df
):
    """
    Save or update behaviour features.
    """

    feature_df = feature_df.fillna(0)

    for row in feature_df.itertuples(index=False):

        behavior = (

            db.query(BehaviorFeature)

            .filter(
                BehaviorFeature.employee_id ==
                row.employee_id
            )

            .first()

        )

        if behavior is None:

            behavior = BehaviorFeature(

                employee_id=row.employee_id

            )

            db.add(behavior)

        # ---------------- Login ----------------

        behavior.login_count = int(row.login_count)

        behavior.unique_pc_count = int(row.unique_pc_count)

        behavior.weekend_logins = int(row.weekend_logins)

        behavior.after_hours_logins = int(row.after_hours_logins)

        behavior.average_login_hour = float(
            row.average_login_hour
        )

        # ---------------- HTTP ----------------

        behavior.http_visit_count = int(row.http_visit_count)

        behavior.unique_websites = int(row.unique_websites)

        behavior.after_hours_http = int(row.after_hours_http)

        behavior.weekend_http = int(row.weekend_http)

        behavior.unique_http_pcs = int(row.unique_http_pcs)

        # ---------------- Email ----------------

        behavior.email_sent = int(row.email_sent)

        behavior.external_emails = int(row.external_emails)

        behavior.after_hours_emails = int(
            row.after_hours_emails
        )

        # ---------------- File ----------------

        behavior.file_access_count = int(
            row.file_access_count
        )

        behavior.unique_files = int(
            row.unique_files
        )

        behavior.after_hours_file_access = int(
            row.after_hours_file_access
        )

        behavior.weekend_file_access = int(
            row.weekend_file_access
        )

        # ---------------- Device ----------------

        behavior.device_usage_count = int(
            row.device_usage_count
        )

        behavior.connect_count = int(
            row.connect_count
        )

        behavior.disconnect_count = int(
            row.disconnect_count
        )

        behavior.after_hours_device_usage = int(
            row.after_hours_device_usage
        )

        behavior.weekend_device_usage = int(
            row.weekend_device_usage
        )

    db.commit()

    print("=" * 60)

    print(
        f"Behavior features saved: {len(feature_df)}"
    )

    print("=" * 60)


# ============================================================
# EMPLOYEE BEHAVIOR REPORT
# ============================================================

def get_employee_behavior_report(
    db: Session,
    employee_id: str
):

    employee = (

        db.query(Employee)

        .filter(
            Employee.employee_id == employee_id
        )

        .first()

    )

    if employee is None:

        return None

    behavior = (

        db.query(BehaviorFeature)

        .filter(
            BehaviorFeature.employee_id ==
            employee_id
        )

        .first()

    )

    predictions = (
    db.query(Prediction)
    .filter(
        Prediction.employee_id == employee_id
    )
    .order_by(
        Prediction.event_timestamp.desc()
    )
    .all()
)

    total_predictions = len(predictions)

    high_risk = sum(

        1

        for p in predictions

        if p.risk_level == "HIGH"

    )

    return {

        "employee": employee,

        "behavior": behavior,

        "predictions": predictions,

        "total_predictions": total_predictions,

        "high_risk": high_risk

    }