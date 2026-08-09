import csv
import io
from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.core.database import get_db
from app.core.security import require_analyst
from app.models import ActivityLog, Employee, ActivityType
from app.schemas import ActivityLogCreate, ActivityLogOut, ActivityLogBulkIngest
from loguru import logger

router = APIRouter(prefix="/activities", tags=["Activity Monitoring"])


def _is_outside_hours(ts: datetime, work_start: int = 8, work_end: int = 18) -> bool:
    """Simple heuristic — refine per employee profile later."""
    return ts.hour < work_start or ts.hour >= work_end or ts.weekday() >= 5


# ─── Log a single activity ───────────────────────────────────────────────────
@router.post("", response_model=ActivityLogOut, status_code=201)
def log_activity(payload: ActivityLogCreate, db: Session = Depends(get_db),
                 _=Depends(require_analyst)):
    emp = db.query(Employee).filter(Employee.id == payload.employee_id).first()
    if not emp:
        raise HTTPException(404, "Employee not found")

    log = ActivityLog(
        **payload.model_dump(),
        is_outside_hours=_is_outside_hours(payload.timestamp),
    )
    db.add(log); db.commit(); db.refresh(log)
    return log


# ─── Bulk ingest (JSON) ──────────────────────────────────────────────────────
@router.post("/bulk", status_code=202)
def bulk_ingest(payload: ActivityLogBulkIngest, background_tasks: BackgroundTasks,
                db: Session = Depends(get_db), _=Depends(require_analyst)):
    background_tasks.add_task(_bulk_insert, payload.logs, db)
    return {"message": f"Queued {len(payload.logs)} activity logs for ingestion"}


def _bulk_insert(logs: list, db: Session):
    objects = []
    for item in logs:
        objects.append(ActivityLog(
            **item.model_dump(),
            is_outside_hours=_is_outside_hours(item.timestamp),
        ))
    db.bulk_save_objects(objects)
    db.commit()
    logger.info(f"Bulk inserted {len(objects)} activity logs")


# ─── CERT Dataset CSV Upload ──────────────────────────────────────────────────
@router.post("/cert/upload/{log_type}")
async def upload_cert_csv(
    log_type: str,
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
    _=Depends(require_analyst),
):
    """
    Upload CERT r4.2 CSV files.
    log_type: logon | file | device | email | http
    Dataset: https://kilthub.cmu.edu/articles/dataset/Insider_Threat_Test_Dataset/12841247
    """
    valid_types = ["logon", "file", "device", "email", "http"]
    if log_type not in valid_types:
        raise HTTPException(400, f"log_type must be one of {valid_types}")

    content = await file.read()
    text = content.decode("utf-8-sig")
    background_tasks.add_task(_process_cert_csv, log_type, text, db)
    return {"message": f"Processing CERT {log_type}.csv in background"}


def _process_cert_csv(log_type: str, content: str, db: Session):
    reader = csv.DictReader(io.StringIO(content))
    CERT_ACTIVITY_MAP = {
        "logon":  {"Logon": ActivityType.login, "Logoff": ActivityType.logout},
        "device": {"Connect": ActivityType.usb_connect, "Disconnect": ActivityType.usb_disconnect},
        "file":   {"open": ActivityType.file_download, "write": ActivityType.file_upload,
                   "copy": ActivityType.data_transfer, "delete": ActivityType.file_delete},
        "email":  {"Send": ActivityType.email_send},
        "http":   {"WWW Visit": ActivityType.application_access},
    }
    activity_map = CERT_ACTIVITY_MAP.get(log_type, {})
    inserted = 0

    for row in reader:
        try:
            user_id_str = row.get("user", "")
            # Try to find matching employee by employee_id field
            emp = db.query(Employee).filter(Employee.employee_id == user_id_str).first()
            if not emp:
                continue

            raw_date = row.get("date", "")
            try:
                ts = datetime.strptime(raw_date, "%m/%d/%Y %H:%M:%S")
                ts = ts.replace(tzinfo=timezone.utc)
            except ValueError:
                continue

            activity_key = row.get("activity", "")
            act_type = activity_map.get(activity_key, ActivityType.application_access)

            log = ActivityLog(
                employee_id=emp.id,
                activity_type=act_type,
                timestamp=ts,
                resource=row.get("filename") or row.get("url") or row.get("to"),
                bytes_transferred=int(row.get("size", 0) or 0),
                is_outside_hours=_is_outside_hours(ts),
                raw_log=dict(row),
            )
            db.add(log)
            inserted += 1

            if inserted % 1000 == 0:
                db.commit()
                logger.info(f"CERT ingest: {inserted} records committed")

        except Exception as e:
            logger.warning(f"Skipping CERT row: {e}")
            continue

    db.commit()
    logger.info(f"CERT {log_type} ingest complete: {inserted} records")


# ─── Query activities ────────────────────────────────────────────────────────
@router.get("", response_model=list[ActivityLogOut])
def list_activities(
    db: Session = Depends(get_db),
    _=Depends(require_analyst),
    employee_id: Optional[int] = Query(None),
    activity_type: Optional[ActivityType] = Query(None),
    is_suspicious: Optional[bool] = Query(None),
    is_outside_hours: Optional[bool] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
):
    q = db.query(ActivityLog)
    if employee_id:
        q = q.filter(ActivityLog.employee_id == employee_id)
    if activity_type:
        q = q.filter(ActivityLog.activity_type == activity_type)
    if is_suspicious is not None:
        q = q.filter(ActivityLog.is_suspicious == is_suspicious)
    if is_outside_hours is not None:
        q = q.filter(ActivityLog.is_outside_hours == is_outside_hours)
    if start_date:
        q = q.filter(ActivityLog.timestamp >= start_date)
    if end_date:
        q = q.filter(ActivityLog.timestamp <= end_date)
    return q.order_by(ActivityLog.timestamp.desc()).offset((page-1)*page_size).limit(page_size).all()


@router.get("/stats/summary")
def activity_summary(
    db: Session = Depends(get_db),
    _=Depends(require_analyst),
    employee_id: Optional[int] = Query(None),
    days: int = Query(7, ge=1, le=90),
):
    since = datetime.now(timezone.utc) - timedelta(days=days)
    q = db.query(ActivityLog).filter(ActivityLog.timestamp >= since)
    if employee_id:
        q = q.filter(ActivityLog.employee_id == employee_id)

    total = q.count()
    suspicious = q.filter(ActivityLog.is_suspicious == True).count()
    outside_hours = q.filter(ActivityLog.is_outside_hours == True).count()

    by_type = (db.query(ActivityLog.activity_type, func.count(ActivityLog.id))
               .filter(ActivityLog.timestamp >= since)
               .group_by(ActivityLog.activity_type).all())

    return {
        "period_days": days,
        "total_activities": total,
        "suspicious_activities": suspicious,
        "outside_hours_activities": outside_hours,
        "by_type": {k: v for k, v in by_type},
    }
