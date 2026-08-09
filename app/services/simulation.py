"""
Real-Time Enterprise Simulator
=============================
Generates mock employee activities, runs continuous threat evaluations, and
broadcasts updates over WebSockets to simulate a live corporate network environment.
"""
import asyncio
import random
import os
from datetime import datetime, timezone, timedelta
from loguru import logger
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.websockets import manager
from app.models import (
    Employee, ActivityLog, ActivityType, RiskScore, RiskCategory, Alert, AlertSeverity, AlertStatus
)
from app.services import ml_service
from app.ml import inference as inf_service

DEMO_MODE = True  # Controlled globally via API

# List of activities to simulate
SIMULATED_ACTIVITIES = [
    ("Login", ActivityType.login, "User logged in to corporate workstation"),
    ("Logout", ActivityType.logout, "User logged out of corporate workstation"),
    ("Failed Login", ActivityType.failed_login, "Multiple failed login attempts on server"),
    ("USB Connected", ActivityType.usb_connect, "External flash drive connected to USB port"),
    ("USB Removed", ActivityType.usb_disconnect, "External flash drive disconnected"),
    ("Large File Download", ActivityType.file_download, "Downloaded repository archive file"),
    ("Database Query", ActivityType.database_query, "Executed query on production client table"),
    ("Cloud Upload", ActivityType.file_upload, "Uploaded documents to backup cloud bucket"),
    ("VPN Login", ActivityType.remote_access, "Established VPN tunnel from external IP"),
    ("Remote Login", ActivityType.remote_access, "RDP session connected to core infrastructure host"),
    ("Password Change", ActivityType.privilege_change, "Changed local workstation password"),
    ("Privilege Escalation", ActivityType.privilege_change, "Workstation local administrator rights granted"),
    ("Sensitive File Access", ActivityType.file_download, "Accessed document in HR payroll share folder"),
    ("Policy Violation", ActivityType.application_access, "Unauthorized application execution attempted"),
    ("Application Installation", ActivityType.application_access, "Installed local development build dependencies"),
    ("Email Attachment Sent", ActivityType.email_send, "Sent email with encrypted archive attachment"),
    ("External Device Connected", ActivityType.usb_connect, "External network storage adapter connected")
]

LOCATIONS = ["New York", "London", "San Francisco", "Chicago", "Tokyo", "Paris", "Sydney"]


def toggle_demo_mode(active: bool) -> bool:
    global DEMO_MODE
    DEMO_MODE = active
    logger.info(f"Demo Mode set to: {DEMO_MODE}")
    return DEMO_MODE


def get_demo_mode_status() -> bool:
    return DEMO_MODE


async def run_simulation_loop():
    """Background task running in the FastAPI process."""
    logger.info("Initializing continuous activity simulation background loop...")
    
    # Wait for startup to complete
    await asyncio.sleep(5)
    
    while True:
        try:
            if not DEMO_MODE:
                await asyncio.sleep(5)
                continue

            db: Session = SessionLocal()
            try:
                # 1. Fetch active employees
                employees = db.query(Employee).filter(Employee.is_active == True).all()
                if not employees:
                    db.close()
                    await asyncio.sleep(5)
                    continue

                # 2. Pick a random employee
                emp = random.choice(employees)

                # Determine if we should generate normal or suspicious scenario
                # Let's seed threat scenarios specifically:
                # EMP001 (Alice) -> IP Theft / Large downloads
                # EMP002 (Bob) -> IT Sabotage / deletes
                # EMP003 (Carol) -> Unusual logins / Failed logins
                # EMP004 (David) -> Data exfil / USB connection
                is_threat_actor = emp.employee_id in ["EMP001", "EMP002", "EMP003", "EMP004"]
                
                # 30% chance of threat actor doing a malicious action, otherwise standard activities
                if is_threat_actor and random.random() < 0.35:
                    if emp.employee_id == "EMP001":
                        act_name, act_type, act_desc = "Large File Download", ActivityType.file_download, "Downloaded source code blueprint repository zip"
                        resource = "/vault/blueprint_v2.zip"
                        bytes_transferred = random.randint(50_000_000, 200_000_000) # 50-200MB
                        is_suspicious = True
                    elif emp.employee_id == "EMP002":
                        act_name, act_type, act_desc = "Privilege Escalation", ActivityType.privilege_change, "Administrator privilege change registered"
                        resource = "system_root/root_access"
                        bytes_transferred = 0
                        is_suspicious = True
                    elif emp.employee_id == "EMP003":
                        act_name, act_type, act_desc = "Failed Login", ActivityType.failed_login, "Multiple failed login attempts detected"
                        resource = "payroll_prod_db"
                        bytes_transferred = 0
                        is_suspicious = True
                    else:
                        act_name, act_type, act_desc = "Cloud Upload", ActivityType.file_upload, "Uploaded compressed files to personal backup drive"
                        resource = "drive.google.com/exfil_archive.rar"
                        bytes_transferred = random.randint(30_000_000, 100_000_000)
                        is_suspicious = True
                else:
                    # Pick a random activity
                    act_name, act_type, act_desc = random.choice(SIMULATED_ACTIVITIES)
                    resource = random.choice(["workstation-01", "internal_portal", "email_exchange", "shared_storage/report.xlsx", "www.github.com"])
                    bytes_transferred = random.randint(1_000, 50_000) if act_type in (ActivityType.file_download, ActivityType.file_upload, ActivityType.data_transfer) else 0
                    is_suspicious = random.random() < 0.05  # 5% baseline anomaly rate

                # Outside hours indicator (if hour is night or weekend)
                ts = datetime.now(timezone.utc)
                is_outside_hours = ts.hour < 8 or ts.hour >= 18 or ts.weekday() >= 5

                # 3. Create activity log
                log = ActivityLog(
                    employee_id=emp.id,
                    activity_type=act_type,
                    timestamp=ts,
                    source_ip=f"192.168.1.{10+emp.id}" if not (emp.employee_id == "EMP003" and is_suspicious) else f"10.0.9.{random.randint(10, 250)}",
                    destination_ip=f"192.168.1.1" if not is_suspicious else f"203.0.113.{random.randint(10, 250)}",
                    resource=resource,
                    bytes_transferred=bytes_transferred,
                    duration_seconds=random.randint(5, 600),
                    is_outside_hours=is_outside_hours,
                    is_suspicious=is_suspicious,
                    raw_log={"simulated": True, "activity_name": act_name, "description": act_desc}
                )
                db.add(log)
                db.commit()
                db.refresh(log)

                # 4. Perform ML Scoring via streaming cache engine
                from app.services.streaming_service import StreamingRiskEngine
                details = {
                    "resource": log.resource,
                    "bytes_transferred": log.bytes_transferred,
                    "is_outside_hours": log.is_outside_hours,
                    "is_suspicious": log.is_suspicious,
                    "duration_seconds": log.duration_seconds,
                    "device_id": log.device_id,
                    "timestamp": log.timestamp.isoformat()
                }
                stream_res = StreamingRiskEngine.predict_stream_event(db, emp.id, log.activity_type.value, details)
                pred = stream_res["prediction"]
                
                # Fetch risk score db object
                rs = db.query(RiskScore).filter(RiskScore.id == stream_res["risk_score_id"]).first()

                # Trigger alert if risk is High or Critical
                new_alert = None
                if rs.risk_category in (RiskCategory.high, RiskCategory.critical):
                    # Fetch that alert
                    latest_alert = db.query(Alert).filter(Alert.employee_id == emp.id).order_by(Alert.triggered_at.desc()).first()
                    if latest_alert:
                        new_alert = {
                            "alert_id": latest_alert.alert_id,
                            "title": latest_alert.title,
                            "severity": latest_alert.severity.value,
                            "status": latest_alert.status.value,
                            "description": latest_alert.description,
                            "triggered_at": latest_alert.triggered_at.isoformat(),
                            "employee_name": emp.full_name,
                            "department": emp.department.name if emp.department else "N/A"
                        }

                # 5. Build broadcast payload
                payload = {
                    "type": "simulation_tick",
                    "activity": {
                        "id": int(log.id),
                        "employee_id": emp.id,
                        "employee_name": emp.full_name,
                        "employee_code": emp.employee_id,
                        "department": emp.department.name if emp.department else "N/A",
                        "activity_type": log.activity_type.value,
                        "activity_name": act_name,
                        "description": act_desc,
                        "timestamp": log.timestamp.isoformat(),
                        "source_ip": log.source_ip,
                        "resource": log.resource,
                        "bytes_transferred": int(log.bytes_transferred or 0),
                        "is_suspicious": bool(log.is_suspicious),
                        "is_outside_hours": bool(log.is_outside_hours)
                    },
                    "risk_score": {
                        "employee_id": emp.id,
                        "employee_name": emp.full_name,
                        "employee_code": emp.employee_id,
                        "department": emp.department.name if emp.department else "N/A",
                        "total_score": rs.total_score,
                        "risk_category": rs.risk_category.value,
                        "trend": rs.trend,
                        "isolation_forest_score": pred["isolation_forest_score"],
                        "xgboost_probability": pred["confidence"],
                        "shap_explanation": pred["shap_explanation"],
                        "recommended_action": pred["recommended_action"],
                        "top_factors": rs.explanation.get("top_factors", [])
                    },
                    "alert": new_alert
                }

                # 6. Broadcast over WebSocket
                await manager.broadcast(payload)
                logger.info(f"Simulation Tick: Activity recorded for {emp.full_name} ({emp.employee_id}) -> Risk: {rs.total_score:.1f}")

            except Exception as inner_e:
                logger.error(f"Error in simulation loop iteration: {inner_e}")
            finally:
                db.close()

        except Exception as outer_e:
            logger.error(f"Simulation loop crashed: {outer_e}")

        # Tick rate is 5 seconds
        await asyncio.sleep(5)
