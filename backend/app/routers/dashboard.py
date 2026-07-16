"""Dashboard aggregation endpoints.

These exist to feed the four dashboards in Module 10. They are all READ-ONLY and all
AGGREGATE - they return counts, trends, and rankings, never raw per-event data. The
raw data already has endpoints (/api/alerts, /api/investigate); duplicating it here
would be two sources of truth for the same fact.

A NOTE ON WHAT IS SAFE TO RETURN, BECAUSE IT IS SUBTLE
-----------------------------------------------------
An alert's `risk_score` is a MODEL OUTPUT. It is the decomposed 0-100 composite the
analyst is supposed to act on. Every role may see it - that is the entire point of
the product.

An employee's `is_insider` flag is GROUND TRUTH - the answer key from CERT. It is
NOT a model output, and it is restricted to managers and administrators (see
/api/data/employees/{id}, which is gated on CAN_VIEW_GROUND_TRUTH).

`top-risks` ranks employees BY THEIR MODEL RISK SCORE and is therefore safe for every
role - but it must never leak `is_insider` in the response, or it becomes a covert
channel to the answer key. It does not. This is checked by a test.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Annotated

from sqlalchemy import Float, cast, desc, func, select
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, Query

from backend.app.dependencies import CurrentUser, get_db
from backend.app.models import Alert, AlertSeverity, Employee

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


# The five risk components the spec's Module 6 defines. Named here so the breakdown
# endpoint returns them in a stable, known order rather than whatever JSON key order
# the database happens to hand back.
RISK_COMPONENTS = [
    "behavioral_anomalies",
    "privilege_misuse",
    "data_access_violations",
    "access_pattern_deviations",
    "historical_security_events",
]


@router.get("/risk-trend", summary="Alert volume and severity over time")
def risk_trend(
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
    days: Annotated[int, Query(ge=1, le=365)] = 90,
) -> dict:
    """Alerts per day, split by severity - the manager's line chart.

    Grouped by the DAY THE BEHAVIOUR HAPPENED (alert_date), not the day the row was
    written, because the question is "when was the organisation at risk", not "when
    did the batch job run".

    Returns a dense series: every day in the window appears, even the zero days.
    A chart with gaps where nothing happened misreads as missing data rather than
    as a quiet day, and the difference matters to someone watching a trend.
    """
    rows = db.execute(
        select(
            Alert.alert_date,
            Alert.severity,
            func.count(),
        )
        .where(Alert.alert_date.isnot(None))
        .group_by(Alert.alert_date, Alert.severity)
        .order_by(Alert.alert_date)
    ).all()

    if not rows:
        return {"days": days, "series": [], "total_alerts": 0}

    # Collapse into {date: {severity: count}}.
    by_day: dict[date, dict[str, int]] = {}
    for d, sev, n in rows:
        by_day.setdefault(d, {})[sev.value] = n

    # Densify from the last day backwards, so the window is exactly `days` long and
    # ends on the most recent alert rather than on today (the CERT data is historical
    # - "today" is 2026, the data is 2010, and an empty 2026 chart helps nobody).
    last_day = max(by_day)
    first_day = last_day - timedelta(days=days - 1)

    severities = [s.value for s in AlertSeverity]
    series = []
    total = 0
    cursor = first_day
    while cursor <= last_day:
        counts = by_day.get(cursor, {})
        point = {"date": cursor.isoformat()}
        for s in severities:
            c = counts.get(s, 0)
            point[s] = c
            total += c
        series.append(point)
        cursor += timedelta(days=1)

    return {
        "days": days,
        "from": first_day.isoformat(),
        "to": last_day.isoformat(),
        "severities": severities,
        "series": series,
        "total_alerts": total,
    }


@router.get("/anomaly-breakdown", summary="Which risk components are driving alerts")
def anomaly_breakdown(
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    """The five risk components, averaged across current alerts - the SOC bar chart.

    This answers "what KIND of risk are we seeing" - is it privilege misuse, data
    access, behavioural anomalies? It reads the `components` JSON that the risk engine
    already wrote onto each alert, so it costs nothing to compute and cannot drift
    from what the analyst sees on the alert itself.

    Averaged, not summed: a sum just reproduces the alert count in five colours. The
    average says which component is TYPICALLY high when an alert fires, which is the
    actual question.
    """
    alerts = db.execute(
        select(Alert.components).where(Alert.severity != AlertSeverity.INFORMATIONAL)
    ).all()

    # Only alerts that actually carry components. Older rows, or rows written before
    # the risk engine existed, may not - and averaging in an implicit zero for them
    # would understate every component equally, which is misleading rather than
    # conservative.
    totals = {c: 0.0 for c in RISK_COMPONENTS}
    n = 0
    for (components,) in alerts:
        if not components:
            continue
        n += 1
        for c in RISK_COMPONENTS:
            totals[c] += float(components.get(c, 0.0))

    if n == 0:
        return {
            "alerts_considered": 0,
            "components": [{"component": c, "average": 0.0} for c in RISK_COMPONENTS],
        }

    breakdown = [
        {"component": c, "average": round(totals[c] / n, 2)} for c in RISK_COMPONENTS
    ]
    # Sorted so the chart reads worst-first without the frontend having to know the
    # component order.
    breakdown.sort(key=lambda x: x["average"], reverse=True)

    return {"alerts_considered": n, "components": breakdown}


@router.get("/top-risks", summary="The riskiest employees right now")
def top_risks(
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
) -> dict:
    """Employees ranked by their PEAK alert risk score - the manager's watch-list.

    Ranks on the highest risk score any of the employee's alerts reached. Peak, not
    average, because a single critical day is the thing a manager needs to see - an
    insider with one 95-scoring day and thirty quiet ones should sit at the TOP of
    this list, and an average would bury him.

    SAFE FOR ALL ROLES. It ranks on risk_score, which is a model output. It returns
    the employee's name, department, and score - it does NOT return is_insider, which
    is ground truth and gated elsewhere. Ranking by model output is exactly what an
    analyst is meant to do; it is not a peek at the answer key.
    """
    rows = db.execute(
        select(
            Alert.user_id,
            func.max(Alert.risk_score).label("peak_risk"),
            func.count().label("alert_count"),
            func.max(Alert.alert_date).label("last_alert"),
        )
        .group_by(Alert.user_id)
        .order_by(desc("peak_risk"))
        .limit(limit)
    ).all()

    if not rows:
        return {"employees": []}

    # One query for the employee metadata, keyed by id, rather than N queries in a
    # loop.
    user_ids = [r.user_id for r in rows]
    employees = {
        e.user_id: e
        for e in db.scalars(select(Employee).where(Employee.user_id.in_(user_ids)))
    }

    out = []
    for r in rows:
        emp = employees.get(r.user_id)
        out.append(
            {
                "user_id": r.user_id,
                "employee_name": emp.employee_name if emp else None,
                "department": emp.department if emp else None,
                "team": emp.team if emp else None,
                "peak_risk_score": round(float(r.peak_risk), 1),
                "alert_count": r.alert_count,
                "last_alert": r.last_alert.isoformat() if r.last_alert else None,
                # DELIBERATELY ABSENT: is_insider. That is ground truth. This endpoint
                # is open to analysts, and leaking it here would be a covert channel
                # to the answer key. See the module docstring.
            }
        )

    return {"employees": out}