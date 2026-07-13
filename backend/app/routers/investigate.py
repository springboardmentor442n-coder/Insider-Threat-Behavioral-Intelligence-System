"""Threat Investigation. Spec Milestone 3, Module 7.

An alert says "look at ABC0174 on the 23rd". An INVESTIGATION answers the question
that immediately follows: what has this person actually been doing?

Three things an analyst needs, and nothing else:

  1. THE TIMELINE.   Every alert for this user, in order, with the risk score. A
                     single bad Tuesday is a Tuesday. Six escalating days is a
                     campaign, and it looks completely different on a chart.

  2. THE EVIDENCE.   The raw behaviour behind the score - USB connects, file events,
                     after-hours logons - next to what is NORMAL FOR THIS PERSON.
                     "Eight USB connections" means nothing. "Eight, against a personal
                     baseline of zero" is the entire case.

  3. THE REASONING.  The SHAP decomposition. Which features drove the score, in which
                     direction, including what argued AGAINST.

ON-DEMAND SCORING IS DELIBERATELY SEPARATE FROM THE QUEUE
---------------------------------------------------------
`POST /investigate/{user_id}/score` runs the model against any user, at any time,
including users nothing has ever flagged - and it does NOT write to the alert table.

That separation matters. An investigation tool that quietly injected speculative
alerts into the SOC queue every time someone got curious would poison the queue, and
the queue is the one thing that has to stay trustworthy.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.dependencies import CurrentUser
from backend.app.features_models import DailyFeatures, UserBaseline
from backend.app.models import Alert, Employee

router = APIRouter(prefix="/api/investigate", tags=["investigation"])


@router.get("/{user_id}", summary="The full case file on one employee")
def investigate(
    user_id: str,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
    days: Annotated[int, Query(ge=1, le=365)] = 90,
) -> dict:
    """Everything known about one employee: timeline, evidence, baseline.

    NOTE WHAT IS NOT RETURNED: `is_insider`.

    That field is the CERT answer key. It is available to Managers through the
    employee endpoint, where it is clearly labelled as ground truth - but it has no
    business being in an INVESTIGATION view, because an investigation is the process
    of forming a judgement and showing the analyst the answer first would make the
    whole exercise theatre.

    In production there IS no answer key. The tool should work the same way here.
    """
    employee = db.get(Employee, user_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="No such employee.")

    alerts = list(
        db.scalars(
            select(Alert)
            .where(Alert.user_id == user_id)
            .order_by(Alert.alert_date.desc())
            .limit(days)
        ).all()
    )

    # The window: anchor on the most recent alert if there is one, otherwise on the
    # most recent day we have data for. Anchoring on TODAY would be wrong - this is a
    # 2010-2011 dataset, and "the last 90 days" from now is an empty chart.
    if alerts:
        anchor = alerts[0].alert_date
    else:
        anchor = db.scalar(
            select(DailyFeatures.date)
            .where(DailyFeatures.user_id == user_id)
            .order_by(DailyFeatures.date.desc())
            .limit(1)
        )
    if anchor is None:
        raise HTTPException(
            status_code=404,
            detail="No behavioural data for this employee. Has build_features run?",
        )

    start = anchor - timedelta(days=days)

    rows = list(
        db.scalars(
            select(DailyFeatures)
            .where(
                DailyFeatures.user_id == user_id,
                DailyFeatures.date >= start,
                DailyFeatures.date <= anchor,
            )
            .order_by(DailyFeatures.date)
        ).all()
    )

    baseline = db.scalar(
        select(UserBaseline).where(UserBaseline.user_id == user_id)
    )

    return {
        "employee": {
            "user_id": employee.user_id,
            "name": employee.employee_name,
            "role": employee.role,
            "department": employee.department,
            "team": employee.team,
            "supervisor": employee.supervisor,
        },
        # THE BASELINE IS THE POINT OF THE WHOLE SYSTEM.
        #
        # "Eight USB connections" is not evidence of anything - plenty of people move
        # files for a living. "Eight, against a personal baseline of zero" is the
        # entire case, and it is the difference between UEBA and a threshold alert.
        "baseline": (
            {
                "training_days": baseline.training_days,
                "mean_logon_count": round(baseline.mean_logon_count, 2),
                "mean_usb_connect": round(baseline.mean_usb_connect, 3),
                "mean_file_events": round(baseline.mean_file_events, 2),
                "mean_after_hours_logon": round(baseline.mean_after_hours_logon, 3),
                "ever_used_usb": baseline.ever_used_usb,
                "ever_worked_after_hours": baseline.ever_worked_after_hours,
            }
            if baseline
            else None
        ),
        "timeline": [
            {
                "date": a.alert_date.isoformat(),
                "severity": a.severity.value,
                "status": a.status.value,
                "risk_score": a.risk_score,
                "ml_probability": a.ml_probability,
                "components": a.components,
                "alert_id": a.id,
            }
            for a in reversed(alerts)
        ],
        "evidence": [
            {
                "date": r.date.isoformat(),
                "logon_count": r.logon_count,
                "after_hours_logon_count": r.after_hours_logon_count,
                "weekend_logon_count": r.weekend_logon_count,
                "distinct_pcs": r.distinct_pcs,
                "session_hours": round(r.total_session_hours, 2),
                "usb_connect_count": r.usb_connect_count,
                "file_event_count": r.file_event_count,
                "exe_file_count": r.exe_file_count,
                "zip_file_count": r.zip_file_count,
                "external_email_count": r.external_email_count,
                "job_site_visits": r.job_site_visits,
                "wikileaks_visits": r.wikileaks_visits,
                "cloud_storage_visits": r.cloud_storage_visits,
                "hacking_site_visits": r.hacking_site_visits,
                "used_supervisor_pc": r.used_supervisor_pc,
            }
            for r in rows
        ],
        "window": {"start": start.isoformat(), "end": anchor.isoformat()},
    }


@router.get("/{user_id}/explain", summary="Why did the model score this day?")
def explain_day(
    user_id: str,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
    day: date,
) -> dict:
    """The SHAP decomposition for one user on one day. Scored on demand.

    Loads the persisted model, rebuilds this user's feature row, and decomposes the
    prediction into per-feature contributions that SUM EXACTLY to it.

    THIS DOES NOT WRITE AN ALERT. An analyst poking at a hypothesis must not be able
    to inject speculative alerts into the SOC queue - the queue is the one thing that
    has to stay trustworthy.
    """
    import numpy as np
    import pandas as pd

    from backend.app.detection import load_feature_frame
    from backend.app.scoring import align_features, explain, load_models

    try:
        xgb, _iso, meta = load_models()
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e

    # The model needs the temporal + deviation features, and those are computed
    # ACROSS TIME - a rolling 14-day mean cannot be reconstructed from a single row.
    # So the whole user's history is loaded and the requested day selected from it.
    df = load_feature_frame(db, user_id=user_id)
    if df.empty:
        raise HTTPException(status_code=404, detail="No behavioural data for that user.")

    from backend.app.detection import (
        BASELINE_TRAINING_DAYS,
        add_deviation_features,
        add_temporal_features,
    )

    df = add_temporal_features(df)
    cutoff = pd.Timestamp(df["date"].min()) + pd.Timedelta(days=BASELINE_TRAINING_DAYS)
    df = add_deviation_features(df, training_cutoff=cutoff)

    target = df[pd.to_datetime(df["date"]).dt.date == day]
    if target.empty:
        raise HTTPException(
            status_code=404,
            detail=f"No data for {user_id} on {day}. The employee may not have worked.",
        )

    X = align_features(target, meta["feature_columns"])
    prob = xgb.predict_proba(X)[:, 1]

    exps = explain(
        xgb, X, meta["feature_columns"],
        [user_id], [day], prob,
    )
    e = exps[0]

    return {
        "user_id": user_id,
        "date": day.isoformat(),
        "probability": round(e.probability, 6),
        "threshold": meta["threshold"],
        "would_alert": bool(e.probability >= meta["threshold"]),
        "baseline_probability": round(float(1 / (1 + np.exp(-e.base_value))), 6),
        # Both directions. A system that only ever shows you the evidence for its own
        # conclusion is not explaining itself, it is lobbying.
        "contributions": [
            {
                "feature": c.feature,
                "value": round(c.value, 3),
                "contribution": round(c.shap_value, 4),
                "direction": c.direction,
            }
            for c in e.top(10)
        ],
    }