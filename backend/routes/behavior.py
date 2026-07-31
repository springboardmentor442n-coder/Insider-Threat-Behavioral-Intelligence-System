from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.config import get_db
from backend.crud import get_employee_behavior_report

router = APIRouter(
    prefix="/behavior",
    tags=["Behavior"]
)


@router.get("/{employee_id}")
def get_employee_behavior(employee_id: str, db: Session = Depends(get_db)):

    report = get_employee_behavior_report(db, employee_id)

    if report is None:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    employee = report["employee"]
    behavior = report["behavior"]

    return {

        "employee": {
            "employee_id": employee.employee_id,
            "name": employee.name,
            "department": employee.department,
            "designation": employee.designation,
            "email": employee.email
        },

        "behavior": None if behavior is None else {

            # -------------------------
            # Login Features
            # -------------------------
            "login_count": behavior.login_count,
            "unique_pc_count": behavior.unique_pc_count,
            "weekend_logins": behavior.weekend_logins,
            "after_hours_logins": behavior.after_hours_logins,
            "average_login_hour": behavior.average_login_hour,

            # -------------------------
            # HTTP Features
            # -------------------------
            "http_visit_count": behavior.http_visit_count,
            "unique_websites": behavior.unique_websites,
            "after_hours_http": behavior.after_hours_http,
            "weekend_http": behavior.weekend_http,
            "unique_http_pcs": behavior.unique_http_pcs,

            # -------------------------
            # Email Features
            # -------------------------
            "email_sent": behavior.email_sent,
            "external_emails": behavior.external_emails,
            "after_hours_emails": behavior.after_hours_emails,

            # -------------------------
            # File Features
            # -------------------------
            "file_access_count": behavior.file_access_count,
            "unique_files": behavior.unique_files,
            "after_hours_file_access": behavior.after_hours_file_access,
            "weekend_file_access": behavior.weekend_file_access,

            # -------------------------
            # Device Features
            # -------------------------
            "device_usage_count": behavior.device_usage_count,
            "connect_count": behavior.connect_count,
            "disconnect_count": behavior.disconnect_count,
            "after_hours_device_usage": behavior.after_hours_device_usage,
            "weekend_device_usage": behavior.weekend_device_usage
        },

        "predictions": [
            {
                "id": p.id,
                "login_count": p.login_count,
                "unique_pc_count": p.unique_pc_count,
                "hour": p.hour,
                "is_weekend": p.is_weekend,
                "prediction": p.prediction,
                "risk_level": p.risk_level,
                "confidence": p.confidence
            }
            for p in report["predictions"]
        ],

        "total_predictions": report["total_predictions"],
        "high_risk": report["high_risk"]
    }