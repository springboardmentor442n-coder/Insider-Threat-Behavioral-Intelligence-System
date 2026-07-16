"""User & Entity Behaviour Analytics (UEBA). Spec Module 8.

The detection layer already compares each person against two references - their
OWN history (a personal z-score) and their PEER GROUP (a department z-score). But
those comparisons live inside the model at scoring time and are never surfaced.
An analyst cannot ask "is this person's USB usage unusual FOR THEIR TEAM?" and get
a straight answer.

This router surfaces that analysis as first-class entity intelligence. For any
employee it answers three UEBA questions, all computed live from daily_features -
no model, no retrain:

  1. PEER STANDING.   For each behaviour, this person's daily average vs their
                      department's average, expressed as a z-score. "3.8 sigma
                      above their team on USB" is a sentence a manager understands.

  2. BEHAVIOURAL DRIFT. The person's recent window vs their own earlier baseline
                      window. A user drifting upward on file activity is a
                      different risk from one who has always been high.

  3. RISK TRAJECTORY. Their alert history over time - the shape of the campaign,
                      not a single day.

Why this is its own module and not part of /investigate: investigation is
reactive ("an alert fired, show me this day"). UEBA is proactive ("show me how
this entity behaves relative to normal") and works on ANYONE, flagged or not.
"""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.dependencies import CurrentUser
from backend.app.models import Employee

router = APIRouter(prefix="/api/entity", tags=["entity analytics"])

# The behaviours we surface peer/drift analytics for. A curated subset of the
# full feature set - the ones a human actually reasons about.
UEBA_FEATURES = [
    ("usb_connect_count", "USB connections"),
    ("after_hours_logon_count", "After-hours logons"),
    ("weekend_logon_count", "Weekend logons"),
    ("file_event_count", "File events"),
    ("exe_file_count", "Executable files"),
    ("zip_file_count", "Archive files"),
    ("external_email_count", "External emails"),
    ("job_site_visits", "Job-site visits"),
    ("cloud_storage_visits", "Cloud-storage visits"),
    ("distinct_pcs", "Distinct machines"),
]

# A department peer-std can be zero (a whole team that never touches USB). Dividing
# by it gives infinity. Floor it - the same guard the detection layer uses.
STD_FLOOR = 0.5


@router.get("/{user_id}", summary="Entity behaviour analytics for one employee")
def entity_analytics(
    user_id: str,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
    recent_days: int = Query(30, ge=7, le=180,
                             description="Size of the recent window for drift"),
):
    """Peer-relative standing, behavioural drift, and risk trajectory for one entity.

    Everything here is computed live from daily_features. Safe for any role: it
    reports behavioural statistics and model-derived risk, never the is_insider
    ground-truth label.
    """
    user_id = user_id.upper()
    employee = db.get(Employee, user_id)
    if employee is None:
        raise HTTPException(404, f"No employee {user_id}")

    # ---- how much history does this entity have? ----
    span = db.execute(text("""
        SELECT MIN(date) AS first, MAX(date) AS last, COUNT(*) AS days
        FROM daily_features WHERE user_id = :uid
    """), {"uid": user_id}).mappings().first()

    if not span or span["days"] == 0:
        return {
            "employee": _employee_block(employee),
            "has_data": False,
            "peer_standing": [],
            "drift": [],
            "trajectory": [],
        }

    peer_standing = _peer_standing(db, user_id, employee.department)
    drift = _drift(db, user_id, span["last"], recent_days)
    trajectory = _trajectory(db, user_id)

    return {
        "employee": _employee_block(employee),
        "has_data": True,
        "window": {
            "first_day": str(span["first"]),
            "last_day": str(span["last"]),
            "days_observed": span["days"],
            "recent_days": recent_days,
        },
        "peer_standing": peer_standing,
        "drift": drift,
        "trajectory": trajectory,
    }


def _employee_block(e: Employee) -> dict:
    return {
        "user_id": e.user_id,
        "name": e.employee_name,
        "role": e.role,
        "department": e.department,
        "team": e.team,
        "supervisor": e.supervisor,
    }


def _peer_standing(db: Session, user_id: str, department: str | None) -> list[dict]:
    """For each behaviour: this user's mean vs their department, as a z-score.

    A positive z means "does more of this than their peers". We rank by the
    absolute z so the most anomalous behaviours surface first - that ordering is
    the whole value to an analyst scanning the list.
    """
    if not department:
        return []

    # Build one query that computes, per feature:
    #   - the user's MEAN and their single highest day (PEAK)
    #   - the peer group's daily mean + std
    # Both the average and the peak matter, and they answer DIFFERENT questions.
    # A sustained campaign shows up in the average. A single-day exfiltration
    # (CERT scenario 1) is invisible in a 200-day average - one bad day barely
    # moves the mean - but screams in the peak. Surfacing only the average would
    # let a one-day attacker hide, so we compute both. Done in SQL so we move
    # numbers, not rows.
    user_terms = ", ".join(
        f"AVG(CASE WHEN df.user_id = :uid THEN df.{col} END) AS u_{col}, "
        f"MAX(CASE WHEN df.user_id = :uid THEN df.{col} END) AS up_{col}"
        for col, _ in UEBA_FEATURES
    )
    peer_terms = ", ".join(
        f"AVG(CASE WHEN df.user_id <> :uid THEN df.{col} END) AS pm_{col}, "
        f"STDDEV(CASE WHEN df.user_id <> :uid THEN df.{col} END) AS ps_{col}"
        for col, _ in UEBA_FEATURES
    )
    row = db.execute(text(f"""
        SELECT {user_terms}, {peer_terms}
        FROM daily_features df
        JOIN employees e ON df.user_id = e.user_id
        WHERE e.department = :dept
    """), {"uid": user_id, "dept": department}).mappings().first()

    out = []
    for col, label in UEBA_FEATURES:
        u = row[f"u_{col}"]
        up = row[f"up_{col}"]
        pm = row[f"pm_{col}"]
        ps = row[f"ps_{col}"]
        if u is None or pm is None:
            continue
        u = float(u); pm = float(pm)
        ps = max(float(ps or 0), STD_FLOOR)
        avg_z = (u - pm) / ps
        # peak day vs the peer daily distribution
        peak_z = ((float(up) - pm) / ps) if up is not None else avg_z
        out.append({
            "feature": col,
            "label": label,
            "user_mean": round(u, 3),
            "user_peak": round(float(up), 3) if up is not None else None,
            "peer_mean": round(pm, 3),
            "peer_z": round(avg_z, 2),       # the sustained/average view
            "peak_z": round(peak_z, 2),      # the worst-single-day view
        })
    # Rank by whichever signal is larger - so a behaviour that is only anomalous
    # on ONE day still rises to the top. This is what stops a single-day attacker
    # from being buried under his own normal days.
    out.sort(key=lambda r: max(abs(r["peer_z"]), abs(r["peak_z"])), reverse=True)
    return out


def _drift(db: Session, user_id: str, last_day, recent_days: int) -> list[dict]:
    """Recent window vs the user's own earlier history, per behaviour.

    'Drift' = recent_mean - prior_mean. A user trending UP on a behaviour is a
    different, and often more urgent, risk than one who is merely consistently
    high. We express it as a percentage change so behaviours on different scales
    are comparable.
    """
    # Compute the cutoff date in Python and pass it as a plain bind param. Doing
    # the interval arithmetic in SQL would need `:last::date`, and the `::` cast
    # operator collides with SQLAlchemy's `:param` syntax - so we avoid it.
    from datetime import timedelta
    cut = last_day - timedelta(days=recent_days)

    rows = db.execute(text(f"""
        SELECT
        {", ".join(
            f"AVG(CASE WHEN df.date >= :cut THEN df.{col} END) AS recent_{col}, "
            f"AVG(CASE WHEN df.date <  :cut THEN df.{col} END) AS prior_{col}"
            for col, _ in UEBA_FEATURES
        )}
        FROM daily_features df
        WHERE df.user_id = :uid
    """), {"uid": user_id, "cut": cut}).mappings().first()

    out = []
    for col, label in UEBA_FEATURES:
        recent = rows[f"recent_{col}"]
        prior = rows[f"prior_{col}"]
        if recent is None or prior is None:
            continue
        recent = float(recent); prior = float(prior)
        delta = recent - prior
        # percentage change, guarding divide-by-zero: if prior was ~0 and recent
        # is not, that is a meaningful "new behaviour" - flag it as such.
        if prior < 1e-6:
            pct = None if recent < 1e-6 else float("inf")
        else:
            pct = (delta / prior) * 100
        out.append({
            "feature": col,
            "label": label,
            "recent_mean": round(recent, 3),
            "prior_mean": round(prior, 3),
            "delta": round(delta, 3),
            "pct_change": (None if pct is None
                           else "new" if pct == float("inf")
                           else round(pct, 1)),
        })
    # biggest upward movers first (None/new treated as large)
    def sortkey(r):
        p = r["pct_change"]
        if p == "new":
            return 1e9
        if p is None:
            return -1e9
        return p
    out.sort(key=sortkey, reverse=True)
    return out


def _trajectory(db: Session, user_id: str) -> list[dict]:
    """The user's alert history over time - date, severity, risk score."""
    rows = db.execute(text("""
        SELECT alert_date, severity, risk_score
        FROM alerts
        WHERE user_id = :uid
        ORDER BY alert_date
    """), {"uid": user_id}).mappings().all()
    return [
        {
            "date": str(r["alert_date"]),
            "severity": r["severity"],
            "risk_score": round(float(r["risk_score"]), 1),
        }
        for r in rows
    ]
