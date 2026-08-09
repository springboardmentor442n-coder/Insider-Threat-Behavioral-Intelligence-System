"""
Anomaly detection, risk scoring, alert management, incident management,
UEBA intelligence, and dashboard endpoints.
"""
from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.core.database import get_db
from app.core.security import require_analyst, require_manager
from app.models import (
    Anomaly, RiskScore, Alert, Incident, Employee, ActivityLog,
    RiskCategory, AlertStatus, AlertSeverity, IncidentStatus
)
from app.schemas import (
    AnomalyOut, AnomalyReview, RiskScoreOut, RiskSummary,
    AlertCreate, AlertUpdate, AlertOut,
    IncidentCreate, IncidentUpdate, IncidentOut,
    DashboardStats, SOCDashboard
)
from app.services import ml_service

# ─── Anomalies ────────────────────────────────────────────────────────────────
anomaly_router = APIRouter(prefix="/anomalies", tags=["Anomaly Detection"])


@anomaly_router.post("/detect/{employee_id}")
def run_detection(employee_id: str, background_tasks: BackgroundTasks,
                  db: Session = Depends(get_db), _=Depends(require_analyst)):
    if employee_id.isdigit():
        emp = db.query(Employee).filter(Employee.id == int(employee_id)).first()
    else:
        emp = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not emp:
        raise HTTPException(404, "Employee not found")
    background_tasks.add_task(ml_service.detect_anomalies, db, emp.id, 1)
    return {"message": f"Anomaly detection queued for employee {emp.employee_id}"}


@anomaly_router.post("/train-model")
def train_model(background_tasks: BackgroundTasks, db: Session = Depends(get_db),
                _=Depends(require_manager)):
    background_tasks.add_task(ml_service.train_isolation_forest, db)
    return {"message": "Classifier training queued"}


@anomaly_router.get("", response_model=list[AnomalyOut])
def list_anomalies(
    db: Session = Depends(get_db), _=Depends(require_analyst),
    employee_id: Optional[int] = Query(None),
    anomaly_type: Optional[str] = Query(None),
    min_score: Optional[float] = Query(None),
    is_confirmed: Optional[bool] = Query(None),
    days: int = Query(7, ge=1, le=90),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
):
    since = datetime.now(timezone.utc) - timedelta(days=days)
    q = db.query(Anomaly).filter(Anomaly.detected_at >= since)
    if employee_id:
        q = q.filter(Anomaly.employee_id == employee_id)
    if anomaly_type:
        q = q.filter(Anomaly.anomaly_type == anomaly_type)
    if min_score is not None:
        q = q.filter(Anomaly.anomaly_score >= min_score)
    if is_confirmed is not None:
        q = q.filter(Anomaly.is_confirmed == is_confirmed)
    return q.order_by(desc(Anomaly.anomaly_score)).offset((page-1)*page_size).limit(page_size).all()


@anomaly_router.put("/{anomaly_id}/review", response_model=AnomalyOut)
def review_anomaly(anomaly_id: int, payload: AnomalyReview,
                   db: Session = Depends(get_db), _=Depends(require_analyst)):
    a = db.query(Anomaly).filter(Anomaly.id == anomaly_id).first()
    if not a:
        raise HTTPException(404, "Anomaly not found")
    a.is_confirmed = payload.is_confirmed
    db.commit(); db.refresh(a)
    return a


# ─── Risk Scores ──────────────────────────────────────────────────────────────
risk_router = APIRouter(prefix="/risk", tags=["Risk Scoring"])


@risk_router.post("/score/{employee_id}", response_model=RiskScoreOut)
def calculate_risk(employee_id: str, db: Session = Depends(get_db),
                   _=Depends(require_analyst)):
    if employee_id.isdigit():
        emp = db.query(Employee).filter(Employee.id == int(employee_id)).first()
    else:
        emp = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not emp:
        raise HTTPException(404, "Employee not found")
    return ml_service.compute_risk_score(db, emp.id)


@risk_router.post("/score-all")
def score_all_employees(background_tasks: BackgroundTasks,
                        db: Session = Depends(get_db), _=Depends(require_manager)):
    background_tasks.add_task(ml_service.run_daily_scoring, db)
    return {"message": "Batch risk scoring queued for all active employees"}


def get_risk_leaderboard(
    db: Session,
    category: Optional[str] = None,
    limit: int = 20,
) -> list[RiskSummary]:
    since_7d = datetime.now(timezone.utc) - timedelta(days=7)

    # Latest score per employee via subquery
    latest_sq = (db.query(
        RiskScore.employee_id,
        func.max(RiskScore.score_date).label("max_date")
    ).group_by(RiskScore.employee_id).subquery())

    q = (db.query(RiskScore, Employee)
         .join(latest_sq, (RiskScore.employee_id == latest_sq.c.employee_id) &
               (RiskScore.score_date == latest_sq.c.max_date))
         .join(Employee, Employee.id == RiskScore.employee_id)
         .order_by(desc(RiskScore.total_score)))

    if category:
        q = q.filter(RiskScore.risk_category == category)

    results = q.limit(limit).all()
    summaries = []
    for rs, emp in results:
        anomaly_count = (db.query(func.count(Anomaly.id))
                         .filter(Anomaly.employee_id == emp.id,
                                 Anomaly.detected_at >= since_7d)
                         .scalar() or 0)
        open_alerts = (db.query(func.count(Alert.id))
                       .filter(Alert.employee_id == emp.id,
                               Alert.status == AlertStatus.open)
                       .scalar() or 0)
        summaries.append(RiskSummary(
            employee_id=emp.id,
            employee_name=emp.full_name,
            current_score=rs.total_score,
            risk_category=rs.risk_category,
            trend=rs.trend,
            anomaly_count_7d=anomaly_count,
            open_alerts=open_alerts,
        ))
    return summaries


@risk_router.get("/leaderboard", response_model=list[RiskSummary])
def risk_leaderboard(
    db: Session = Depends(get_db), _=Depends(require_analyst),
    category: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
):
    return get_risk_leaderboard(db, category, limit)


@risk_router.get("/{employee_id}/history", response_model=list[RiskScoreOut])
def risk_history(employee_id: str, days: int = Query(30, ge=7, le=365),
                 db: Session = Depends(get_db), _=Depends(require_analyst)):
    if employee_id.isdigit():
        emp = db.query(Employee).filter(Employee.id == int(employee_id)).first()
    else:
        emp = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not emp:
        raise HTTPException(404, "Employee not found")
    since = datetime.now(timezone.utc) - timedelta(days=days)
    return (db.query(RiskScore)
            .filter(RiskScore.employee_id == emp.id,
                    RiskScore.score_date >= since)
            .order_by(RiskScore.score_date)
            .all())


# ─── Alerts ───────────────────────────────────────────────────────────────────
alert_router = APIRouter(prefix="/alerts", tags=["Alert Management"])


@alert_router.post("", response_model=AlertOut, status_code=201)
def create_alert(payload: AlertCreate, db: Session = Depends(get_db),
                 _=Depends(require_analyst)):
    count = db.query(func.count(Alert.id)).scalar() or 0
    alert_id = f"ALT-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{count+1:04d}"
    alert = Alert(alert_id=alert_id, **payload.model_dump())
    db.add(alert); db.commit(); db.refresh(alert)
    return alert


@alert_router.get("", response_model=list[AlertOut])
def list_alerts(
    db: Session = Depends(get_db), _=Depends(require_analyst),
    status: Optional[AlertStatus] = Query(None),
    severity: Optional[AlertSeverity] = Query(None),
    employee_id: Optional[int] = Query(None),
    days: int = Query(7, ge=1, le=90),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
):
    since = datetime.now(timezone.utc) - timedelta(days=days)
    q = db.query(Alert).filter(Alert.triggered_at >= since)
    if status:
        q = q.filter(Alert.status == status)
    if severity:
        q = q.filter(Alert.severity == severity)
    if employee_id:
        q = q.filter(Alert.employee_id == employee_id)
    return q.order_by(desc(Alert.triggered_at)).offset((page-1)*page_size).limit(page_size).all()


@alert_router.put("/{alert_id}", response_model=AlertOut)
def update_alert(alert_id: int, payload: AlertUpdate, db: Session = Depends(get_db),
                 _=Depends(require_analyst)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(404, "Alert not found")
    now = datetime.now(timezone.utc)
    for k, v in payload.model_dump(exclude_none=True).items():
        setattr(alert, k, v)
    if payload.status == AlertStatus.acknowledged and not alert.acknowledged_at:
        alert.acknowledged_at = now
    if payload.status in (AlertStatus.resolved, AlertStatus.false_positive):
        alert.resolved_at = now
    db.commit(); db.refresh(alert)
    return alert


# ─── Incidents ────────────────────────────────────────────────────────────────
incident_router = APIRouter(prefix="/incidents", tags=["Incident Management"])


@incident_router.post("", response_model=IncidentOut, status_code=201)
def create_incident(payload: IncidentCreate, db: Session = Depends(get_db),
                    _=Depends(require_analyst)):
    count = db.query(func.count(Incident.id)).scalar() or 0
    inc_id = f"INC-{datetime.now(timezone.utc).strftime('%Y')}-{count+1:04d}"
    data = payload.model_dump(exclude={"alert_ids"})
    incident = Incident(incident_id=inc_id, **data)
    db.add(incident); db.flush()

    # Link alerts
    if payload.alert_ids:
        alerts = db.query(Alert).filter(Alert.id.in_(payload.alert_ids)).all()
        for a in alerts:
            a.incident_id = incident.id

    db.commit(); db.refresh(incident)
    return incident


@incident_router.get("", response_model=list[IncidentOut])
def list_incidents(
    db: Session = Depends(get_db), _=Depends(require_analyst),
    status: Optional[IncidentStatus] = Query(None),
    severity: Optional[AlertSeverity] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    q = db.query(Incident)
    if status:
        q = q.filter(Incident.status == status)
    if severity:
        q = q.filter(Incident.severity == severity)
    return q.order_by(desc(Incident.opened_at)).offset((page-1)*page_size).limit(page_size).all()


@incident_router.get("/{incident_id}/timeline")
def get_incident_timeline(incident_id: int, db: Session = Depends(get_db),
                          _=Depends(require_analyst)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(404, "Incident not found")
    if not incident.employee_id:
        return {"timeline": []}

    # Reconstruct activity timeline ±24h around incident open
    window_start = incident.opened_at - timedelta(hours=24)
    activities = (db.query(ActivityLog)
                  .filter(ActivityLog.employee_id == incident.employee_id,
                          ActivityLog.timestamp >= window_start,
                          ActivityLog.timestamp <= incident.opened_at)
                  .order_by(ActivityLog.timestamp)
                  .limit(200)
                  .all())
    return {
        "incident_id": incident.incident_id,
        "employee_id": incident.employee_id,
        "timeline": [{
            "timestamp": a.timestamp.isoformat(),
            "activity_type": a.activity_type.value,
            "resource": a.resource,
            "is_suspicious": a.is_suspicious,
            "is_outside_hours": a.is_outside_hours,
        } for a in activities]
    }


@incident_router.put("/{incident_id}", response_model=IncidentOut)
def update_incident(incident_id: int, payload: IncidentUpdate,
                    db: Session = Depends(get_db), _=Depends(require_analyst)):
    inc = db.query(Incident).filter(Incident.id == incident_id).first()
    if not inc:
        raise HTTPException(404, "Incident not found")
    for k, v in payload.model_dump(exclude_none=True).items():
        setattr(inc, k, v)
    if payload.status == IncidentStatus.resolved and not inc.resolved_at:
        inc.resolved_at = datetime.now(timezone.utc)
    db.commit(); db.refresh(inc)
    return inc


# ─── Dashboard ────────────────────────────────────────────────────────────────
dashboard_router = APIRouter(prefix="/dashboard", tags=["Dashboard & Analytics"])


@dashboard_router.get("/security-analyst", response_model=DashboardStats)
def analyst_dashboard(db: Session = Depends(get_db), _=Depends(require_analyst)):
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    since_7d = now - timedelta(days=7)

    total_monitored = db.query(func.count(Employee.id)).filter(Employee.is_active == True).scalar() or 0

    def count_by_category(cat):
        return (db.query(func.count(RiskScore.employee_id.distinct()))
                .filter(RiskScore.risk_category == cat)
                .scalar() or 0)

    open_alerts = db.query(func.count(Alert.id)).filter(Alert.status == AlertStatus.open).scalar() or 0
    open_incidents = db.query(func.count(Incident.id)).filter(
        Incident.status.in_([IncidentStatus.open, IncidentStatus.in_progress])).scalar() or 0
    anomalies_today = db.query(func.count(Anomaly.id)).filter(Anomaly.detected_at >= today_start).scalar() or 0
    anomalies_7d = db.query(func.count(Anomaly.id)).filter(Anomaly.detected_at >= since_7d).scalar() or 0
    activity_24h = db.query(func.count(ActivityLog.id)).filter(
        ActivityLog.timestamp >= now - timedelta(hours=24)).scalar() or 0

    alert_by_sev = {
        sev.value: db.query(func.count(Alert.id)).filter(
            Alert.severity == sev, Alert.status == AlertStatus.open).scalar() or 0
        for sev in AlertSeverity
    }

    top_risk = get_risk_leaderboard(db=db, limit=5)

    return DashboardStats(
        total_employees_monitored=total_monitored,
        critical_risk_count=count_by_category(RiskCategory.critical),
        high_risk_count=count_by_category(RiskCategory.high),
        medium_risk_count=count_by_category(RiskCategory.medium),
        low_risk_count=count_by_category(RiskCategory.low),
        open_alerts_count=open_alerts,
        open_incidents_count=open_incidents,
        anomalies_today=anomalies_today,
        anomalies_7d=anomalies_7d,
        top_risk_employees=top_risk,
        alert_by_severity=alert_by_sev,
        activity_volume_24h=activity_24h,
    )


@dashboard_router.get("/soc", response_model=SOCDashboard)
def soc_dashboard(db: Session = Depends(get_db), _=Depends(require_analyst)):
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    since_7d = now - timedelta(days=7)

    active_threats = db.query(func.count(Alert.id)).filter(
        Alert.status.in_([AlertStatus.open, AlertStatus.investigating])).scalar() or 0
    anomalies_today = db.query(func.count(Anomaly.id)).filter(
        Anomaly.detected_at >= today_start).scalar() or 0
    active_investigations = db.query(func.count(Incident.id)).filter(
        Incident.status == IncidentStatus.in_progress).scalar() or 0

    # MTTD: mean time from activity log to alert creation (hours)
    mttd = 2.5  # placeholder — compute from alert/activity correlation in prod

    # Anomaly trend: count per day for last 7 days
    trend = []
    for i in range(7):
        day = (today_start - timedelta(days=6-i))
        count = db.query(func.count(Anomaly.id)).filter(
            Anomaly.detected_at >= day,
            Anomaly.detected_at < day + timedelta(days=1)
        ).scalar() or 0
        trend.append({"date": day.date().isoformat(), "anomaly_count": count})

    recent_alerts = (db.query(Alert)
                     .filter(Alert.triggered_at >= since_7d)
                     .order_by(desc(Alert.triggered_at))
                     .limit(10).all())

    return {
        "active_threats": active_threats,
        "behavioral_anomalies_today": anomalies_today,
        "active_investigations": active_investigations,
        "mean_time_to_detect_hours": mttd,
        "mean_time_to_respond_hours": mttd * 2,
        "recent_alerts": recent_alerts,
        "anomaly_trend_7d": trend,
    }


@dashboard_router.get("/manager")
def manager_dashboard(db: Session = Depends(get_db), _=Depends(require_manager)):
    total_employees = db.query(func.count(Employee.id)).filter(Employee.is_active == True).scalar() or 0
    terminated_30d = db.query(func.count(Employee.id)).filter(
        Employee.termination_date >= datetime.now(timezone.utc) - timedelta(days=30)).scalar() or 0
    resolved_incidents = db.query(func.count(Incident.id)).filter(
        Incident.status == IncidentStatus.resolved).scalar() or 0

    risk_distribution = {
        cat.value: db.query(func.count(RiskScore.employee_id.distinct()))
                     .filter(RiskScore.risk_category == cat).scalar() or 0
        for cat in RiskCategory
    }

    return {
        "total_employees_monitored": total_employees,
        "terminated_last_30d": terminated_30d,
        "resolved_incidents_total": resolved_incidents,
        "organizational_risk_distribution": risk_distribution,
        "compliance_status": "operational",
    }
