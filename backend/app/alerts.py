"""Alert generation. Spec Milestone 3, Module 9.

TWO WAYS ALERTS GET MADE, AND THEY ARE NOT THE SAME JOB
-------------------------------------------------------
  BATCH      A nightly run scores every employee for every day it has not scored
             yet, and writes alerts. This is what fills the SOC queue - the thing an
             analyst opens in the morning.

  ON-DEMAND  An analyst asks "score ABC0174 for me, now". This is investigation, not
             monitoring: it does not touch the queue, and it can be run against any
             user at any time, including users nothing has ever flagged.

They share the scoring code and nothing else, because they answer different
questions. Conflating them is how you end up with an investigation tool that
silently pollutes the alert queue with speculative alerts nobody asked for.

RE-RUNNING MUST NOT DESTROY HUMAN JUDGEMENT
--------------------------------------------
Batch jobs get re-run. After a retrain. After a bug fix. After somebody fat-fingers a
date range. The alert table has a UNIQUE constraint on (user_id, alert_date), and
this module UPSERTS: a re-run refreshes the SCORE and leaves the analyst's
assignment, notes, and verdict exactly where they were.

Without that, every re-run duplicates the whole queue, an analyst finds the same
alert four times, and the only remedy is a DELETE against production. And the
alternative failure - deleting and recreating - is worse: it silently throws away
every verdict a human ever recorded, which is the single most valuable data this
system produces.
"""

from __future__ import annotations

import logging
from datetime import date

import numpy as np
import pandas as pd
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from backend.app.models import Alert, AlertSeverity
from backend.app.risk import (
    THRESHOLDS,
    RiskLevel,
    compute_prior_alerts,
    score as risk_score,
)

logger = logging.getLogger(__name__)

# The lowest score worth a row for a user we are ALREADY watching.
#
# Below MEDIUM (20) but above nothing: a quiet-ish day for someone with an open alert
# is evidence about a pattern. The same day for an employee nobody has ever flagged is
# one of a hundred thousand, and writing it down helps no one.
LOW_FLOOR = 10.0


# How many days either side of a real alert count as CONTEXT.
#
# The first version of this made EVERY day of a flagged user informational - so an
# employee with 500 days of history generated 500 context rows, and the table filled
# with 3,180 informational alerts on a dataset with 21 insiders.
#
# That is not context, it is a second copy of the feature table. An investigator wants
# the days AROUND the incident - what led up to it, what happened after - not the
# person's entire employment history. Thirty days either side is a fortnight of
# run-up and a fortnight of aftermath, which is the shape of an actual investigation.
CONTEXT_WINDOW_DAYS = 30


def severity_for(
    risk: float,
    in_case_window: bool,
) -> AlertSeverity | None:
    """Map a risk score to one of the spec's FIVE severities - or to nothing.

    Returning None is the important case, and it is MOST of them. Roughly 99.7% of
    user-days deserve no alert at all. A system that insists on writing a row for
    every one of them has not been thorough, it has been useless: an alert table in
    which 99.7% of the rows are noise is just the feature table with worse ergonomics.
    """
    if risk >= THRESHOLDS[RiskLevel.CRITICAL]:
        return AlertSeverity.CRITICAL
    if risk >= THRESHOLDS[RiskLevel.HIGH]:
        return AlertSeverity.HIGH
    if risk >= THRESHOLDS[RiskLevel.MEDIUM]:
        return AlertSeverity.MEDIUM

    # Below MEDIUM, a row only exists as CONTEXT for a nearby real alert.
    if in_case_window:
        if risk >= LOW_FLOOR:
            return AlertSeverity.LOW
        return AlertSeverity.INFORMATIONAL

    return None


def build_alert_rows(
    df: pd.DataFrame,
    ml_probability: np.ndarray,
    explanations: list | None = None,
) -> list[dict]:
    """Turn scored user-days into alert rows.

    TWO PASSES, AND THE ORDER MATTERS.

    Pass 1 finds every user with at least one MEDIUM+ day. Pass 2 assigns severities,
    and only THEN can a LOW or INFORMATIONAL row exist - because those severities are
    defined relative to whether the user has a case at all.

    Doing it in one pass would mean the severity of a Tuesday depended on whether the
    Friday had been processed yet, which is the kind of order-dependence that produces
    a different answer every time you run it.
    """
    prior = compute_prior_alerts(df, ml_probability)
    scored = risk_score(df, ml_probability, prior_alerts=prior)

    rs = scored["risk_score"].to_numpy()
    users = df["user_id"].to_numpy()
    dates = pd.to_datetime(df["date"]).dt.date.to_numpy()

    # PASS 1: WHERE are the cases? Not just which users - which DAYS.
    #
    # A case is a (user, date) neighbourhood, not a user. Treating it as a user was
    # the bug: it made every day of that person's career "context", and the table
    # filled with thousands of informational rows describing perfectly ordinary
    # Tuesdays from eight months before the incident.
    flagged = rs >= THRESHOLDS[RiskLevel.MEDIUM]
    case_days: dict[str, list] = {}
    for u, d in zip(users[flagged], dates[flagged], strict=True):
        case_days.setdefault(str(u), []).append(d)

    def _in_window(u: str, d) -> bool:
        anchors = case_days.get(u)
        if not anchors:
            return False
        return any(abs((d - a).days) <= CONTEXT_WINDOW_DAYS for a in anchors)

    # SHAP, keyed by (user, date) so we can attach the right explanation to the right
    # row without relying on positional alignment - which breaks the first time
    # anyone sorts or filters the frame.
    shap_by_key: dict[tuple, list] = {}
    if explanations:
        for e in explanations:
            key = (e.user_id, e.date if isinstance(e.date, date) else pd.Timestamp(e.date).date())
            shap_by_key[key] = [
                {
                    "feature": c.feature,
                    "value": round(c.value, 3),
                    "contribution": round(c.shap_value, 4),
                }
                for c in e.top(6)
            ]

    comp_cols = [
        "behavioral_anomalies",
        "privilege_misuse",
        "data_access_violations",
        "access_pattern_deviations",
        "historical_security_events",
    ]

    rows: list[dict] = []
    for i in range(len(df)):
        sev = severity_for(float(rs[i]), _in_window(str(users[i]), dates[i]))
        if sev is None:
            continue

        rows.append(
            {
                "user_id": str(users[i]),
                "alert_date": dates[i],
                "severity": sev,
                "risk_score": round(float(rs[i]), 2),
                "ml_probability": round(float(ml_probability[i]), 6),
                "components": {
                    c: round(float(scored[c].iloc[i]), 1) for c in comp_cols
                },
                "top_features": shap_by_key.get((str(users[i]), dates[i]), []),
            }
        )
    return rows


def persist_alerts(db: Session, rows: list[dict]) -> dict:
    """UPSERT alerts, PRESERVING every trace of human work.

    THE `set_` CLAUSE IS THE WHOLE POINT OF THIS FUNCTION.

    On conflict it updates the SCORE fields and NOTHING ELSE. status, assigned_to_id,
    acknowledged_*, resolved_*, resolution_note are all absent from the update - so a
    re-run after a retrain refreshes the numbers and leaves the analyst's verdict,
    assignment and notes exactly as they were.

    The tempting alternative - DELETE then INSERT - is a catastrophe wearing the
    costume of simplicity. It silently destroys every verdict a human ever recorded,
    which is the only ground truth that exists in production and the training signal
    for the next model.
    """
    if not rows:
        return {"inserted": 0, "updated": 0}

    before = db.scalar(select(Alert.id).limit(1))

    stmt = pg_insert(Alert).values(rows)
    stmt = stmt.on_conflict_do_update(
        constraint="uq_alert_user_day",
        set_={
            "severity": stmt.excluded.severity,
            "risk_score": stmt.excluded.risk_score,
            "ml_probability": stmt.excluded.ml_probability,
            "components": stmt.excluded.components,
            "top_features": stmt.excluded.top_features,
            # DELIBERATELY ABSENT: status, assigned_to_id, acknowledged_*, resolved_*,
            # resolution_note. Re-running the detector must never overwrite what a
            # human decided.
        },
    )
    db.execute(stmt)
    db.commit()

    total = db.scalar(select(Alert.id).order_by(Alert.id.desc()).limit(1)) or 0
    logger.info("Persisted %d alert rows", len(rows))
    return {"written": len(rows), "first_id": before, "last_id": total}


def summarise(db: Session) -> dict:
    """What is actually in the queue right now?"""
    from sqlalchemy import func

    rows = db.execute(
        select(Alert.severity, Alert.status, func.count())
        .group_by(Alert.severity, Alert.status)
    ).all()

    out: dict = {"by_severity": {}, "by_status": {}, "total": 0}
    for sev, status, n in rows:
        sev_k = sev.value if hasattr(sev, "value") else str(sev)
        st_k = status.value if hasattr(status, "value") else str(status)
        out["by_severity"][sev_k] = out["by_severity"].get(sev_k, 0) + n
        out["by_status"][st_k] = out["by_status"].get(st_k, 0) + n
        out["total"] += n
    return out