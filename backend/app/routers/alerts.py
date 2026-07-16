"""The SOC alert queue. Spec Milestone 3, Module 9.

This is the screen an analyst lives in. Everything here is shaped by one question:
what does a person with forty alerts and a coffee actually need?

  * A queue sorted by SEVERITY, then by date. Not by id, not by insertion order.
  * Filters that match how triage actually happens ("show me unassigned criticals").
  * A workflow that records WHO decided WHAT, and WHEN.
  * A resolution that distinguishes TRUE positive from FALSE positive - because that
    distinction is the only ground truth that exists in production, and throwing it
    away means the system can never be measured or improved again.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import case, func, select
from sqlalchemy.orm import Session, selectinload

from backend.app.database import get_db
from backend.app.dependencies import CurrentUser, require_roles
from backend.app.models import (
    Alert,
    AlertNote,
    AlertSeverity,
    AlertStatus,
    AuditLog,
    SecurityUser,
    UserRole,
)
from backend.app.schemas import (
    AlertAssign,
    AlertDetailResponse,
    AlertNoteCreate,
    AlertNoteResponse,
    AlertResolve,
    AlertResponse,
    AlertSummaryResponse,
)

router = APIRouter(prefix="/api/alerts", tags=["alerts"])

logger = logging.getLogger(__name__)

# Who may CLOSE an alert.
#
# Not everyone. Resolving an alert as a false positive is a decision to stop looking
# at somebody - and on a platform that surveils a thousand employees, "stop looking"
# is exactly the button an insider would most like to press about themselves. So it
# takes a Manager or an Administrator, and it is written to the audit log with a name
# on it.
CAN_RESOLVE = (UserRole.SECURITY_MANAGER, UserRole.ADMINISTRATOR)

# Severity ordering for the queue. An enum sorts alphabetically, which would put
# "critical" after "acknowledged" and before "high", and an analyst would open their
# queue to find informational alerts at the top.
_SEVERITY_RANK = {
    AlertSeverity.CRITICAL: 0,
    AlertSeverity.HIGH: 1,
    AlertSeverity.MEDIUM: 2,
    AlertSeverity.LOW: 3,
    AlertSeverity.INFORMATIONAL: 4,
}

_OPEN_STATES = (
    AlertStatus.NEW,
    AlertStatus.ACKNOWLEDGED,
    AlertStatus.INVESTIGATING,
    AlertStatus.ESCALATED,
)


def _audit(db: Session, *, action: str, user_id: int, detail: str, request: Request):
    db.add(
        AuditLog(
            security_user_id=user_id,
            action=action,
            detail=detail,
            ip_address=request.client.host if request.client else None,
        )
    )


@router.get("", response_model=list[AlertResponse], summary="The triage queue")
def list_alerts(
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
    severity: AlertSeverity | None = None,
    status_filter: Annotated[AlertStatus | None, Query(alias="status")] = None,
    user_id: str | None = None,
    assigned_to_me: bool = False,
    unassigned: bool = False,
    open_only: bool = True,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[Alert]:
    """The queue, ordered the way a human triages: worst first, then oldest.

    `open_only` defaults to TRUE. An analyst opening their queue wants the work, not
    the archive - and a queue that shows resolved alerts by default is a queue that
    grows forever and gets ignored by March.
    """
    stmt = select(Alert)

    if open_only and status_filter is None:
        stmt = stmt.where(Alert.status.in_(_OPEN_STATES))
    if status_filter is not None:
        stmt = stmt.where(Alert.status == status_filter)
    if severity is not None:
        stmt = stmt.where(Alert.severity == severity)
    if user_id:
        stmt = stmt.where(Alert.user_id == user_id)
    if assigned_to_me:
        stmt = stmt.where(Alert.assigned_to_id == current_user.id)
    if unassigned:
        stmt = stmt.where(Alert.assigned_to_id.is_(None))

    # Worst first. Sorting by the enum column directly would be ALPHABETICAL, which
    # puts "critical" between "acknowledged" and "high" and "informational" above
    # "low" - an analyst would open their queue to find informational alerts at the
    # top of it. So the order is stated explicitly.
    severity_order = case(
        {sev.value: rank for sev, rank in _SEVERITY_RANK.items()},
        value=Alert.severity,
        else_=99,
    )
    stmt = stmt.order_by(
        severity_order, Alert.alert_date.desc(), Alert.risk_score.desc()
    )

    return list(db.scalars(stmt.limit(limit).offset(offset)).all())


@router.get("/summary", response_model=AlertSummaryResponse, summary="Queue health")
def alert_summary(
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    """Counts by severity and status. The number a manager looks at first."""
    rows = db.execute(
        select(Alert.severity, Alert.status, func.count()).group_by(
            Alert.severity, Alert.status
        )
    ).all()

    by_sev: dict[str, int] = {}
    by_status: dict[str, int] = {}
    total = 0
    for sev, st, n in rows:
        by_sev[sev.value] = by_sev.get(sev.value, 0) + n
        by_status[st.value] = by_status.get(st.value, 0) + n
        total += n

    open_n = sum(by_status.get(s.value, 0) for s in _OPEN_STATES)
    unassigned = db.scalar(
        select(func.count())
        .select_from(Alert)
        .where(Alert.assigned_to_id.is_(None), Alert.status.in_(_OPEN_STATES))
    )
    return {
        "total": total,
        "open": open_n,
        "unassigned_open": int(unassigned or 0),
        "by_severity": by_sev,
        "by_status": by_status,
    }


@router.get("/{alert_id}", response_model=AlertDetailResponse, summary="One alert, with its evidence")
def get_alert(
    alert_id: int,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> Alert:
    """The full alert: the five risk components, the SHAP features, and the notes.

    THIS is the thing that makes an alert actionable rather than merely alarming.
    `components` says WHICH category drove the score; `top_features` says which
    specific behaviours, with numbers, and in which direction - including what argued
    AGAINST the alert. An analyst who can see that a heavy USB user had no
    exfiltration signal closes it in five seconds instead of spending an hour
    reconstructing the case by hand.
    """
    alert = db.scalar(
        select(Alert).options(selectinload(Alert.notes)).where(Alert.id == alert_id)
    )
    if alert is None:
        raise HTTPException(status_code=404, detail="No such alert.")
    return alert


@router.post("/{alert_id}/acknowledge", response_model=AlertResponse, summary="I have seen this")
def acknowledge(
    alert_id: int,
    request: Request,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> Alert:
    """Mark an alert as seen. The first step of triage.

    Idempotent by design: acknowledging an already-acknowledged alert is not an error.
    An API that 409s because somebody double-clicked is an API that teaches people to
    stop clicking.
    """
    alert = db.get(Alert, alert_id)
    if alert is None:
        raise HTTPException(status_code=404, detail="No such alert.")

    if alert.status == AlertStatus.NEW:
        alert.status = AlertStatus.ACKNOWLEDGED
        alert.acknowledged_at = datetime.now(UTC).replace(tzinfo=None)
        alert.acknowledged_by_id = current_user.id
        _audit(db, action="alert.acknowledge", user_id=current_user.id,
               detail=f"alert={alert_id} subject={alert.user_id}", request=request)
        db.commit()
        db.refresh(alert)
    return alert


@router.post("/{alert_id}/assign", response_model=AlertResponse, summary="Assign to an analyst")
def assign(
    alert_id: int,
    payload: AlertAssign,
    request: Request,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> Alert:
    """Assign an alert. Passing null un-assigns it back to the pool."""
    alert = db.get(Alert, alert_id)
    if alert is None:
        raise HTTPException(status_code=404, detail="No such alert.")

    if payload.assignee_id is not None:
        assignee = db.get(SecurityUser, payload.assignee_id)
        if assignee is None or not assignee.is_active:
            raise HTTPException(
                status_code=422,
                detail="That operator does not exist or is deactivated. "
                       "Assigning work to a disabled account is how alerts go to die.",
            )

    alert.assigned_to_id = payload.assignee_id
    if alert.status == AlertStatus.NEW and payload.assignee_id is not None:
        alert.status = AlertStatus.ACKNOWLEDGED

    _audit(db, action="alert.assign", user_id=current_user.id,
           detail=f"alert={alert_id} -> operator={payload.assignee_id}", request=request)
    db.commit()
    db.refresh(alert)
    return alert


@router.post("/{alert_id}/investigate", response_model=AlertResponse, summary="Start investigating")
def start_investigating(
    alert_id: int,
    request: Request,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> Alert:
    alert = db.get(Alert, alert_id)
    if alert is None:
        raise HTTPException(status_code=404, detail="No such alert.")
    if alert.status in (AlertStatus.RESOLVED_TRUE_POSITIVE,
                        AlertStatus.RESOLVED_FALSE_POSITIVE):
        raise HTTPException(
            status_code=409,
            detail="That alert is already resolved. Re-open it by escalating.",
        )

    alert.status = AlertStatus.INVESTIGATING
    if alert.assigned_to_id is None:
        alert.assigned_to_id = current_user.id  # you touched it, you own it
    _audit(db, action="alert.investigate", user_id=current_user.id,
           detail=f"alert={alert_id} subject={alert.user_id}", request=request)
    db.commit()
    db.refresh(alert)
    return alert


@router.post("/{alert_id}/escalate", response_model=AlertResponse, summary="Escalate")
def escalate(
    alert_id: int,
    request: Request,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> Alert:
    """Escalate. Also the way to RE-OPEN a resolved alert.

    New evidence arrives after an alert was closed. It has to be possible to re-open
    it, and it has to be visible that somebody did - a resolution that can be quietly
    reversed with no trace is not a resolution.
    """
    alert = db.get(Alert, alert_id)
    if alert is None:
        raise HTTPException(status_code=404, detail="No such alert.")

    was = alert.status.value
    alert.status = AlertStatus.ESCALATED
    _audit(db, action="alert.escalate", user_id=current_user.id,
           detail=f"alert={alert_id} from={was} subject={alert.user_id}", request=request)
    db.commit()
    db.refresh(alert)

    # Notify oversight + the alert's owner that this was escalated. Best-effort:
    # a notification failure must never break the escalation itself, so it is
    # wrapped and swallowed - the status change is the thing that has to succeed.
    try:
        from backend.app.notifications import on_alert_escalated
        on_alert_escalated(db, alert=alert, actor_id=current_user.id)
    except Exception:  # noqa: BLE001 - notification is a side effect, not the action
        logger.warning("escalation notification failed for alert %s", alert_id)

    return alert


@router.post(
    "/{alert_id}/resolve",
    response_model=AlertResponse,
    dependencies=[Depends(require_roles(*CAN_RESOLVE))],
    summary="Close an alert (manager/admin only)",
)
def resolve(
    alert_id: int,
    payload: AlertResolve,
    request: Request,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> Alert:
    """Close an alert as a TRUE or FALSE positive.

    WHY THE VERDICT IS SPLIT, AND WHY IT IS THE MOST VALUABLE FIELD IN THE SYSTEM.

    A single "closed" state would discard the analyst's judgement. That judgement is
    the ONLY ground truth that exists in production - CERT ships an answer key,
    reality does not. It is how you measure precision on live traffic, it is how you
    notice the model rotting, and it is the training signal for the next one.

    A detection system that does not record what its humans decided can never improve
    and can never tell you it is getting worse.

    WHY IT IS MANAGER-ONLY.

    Resolving as a false positive is a decision to STOP LOOKING at somebody. On a
    platform that watches a thousand employees, "stop looking at me" is precisely the
    button an insider would most like to press about themselves. So it needs a
    Manager, and it lands in the audit log with a name attached.
    """
    alert = db.get(Alert, alert_id)
    if alert is None:
        raise HTTPException(status_code=404, detail="No such alert.")

    alert.status = (
        AlertStatus.RESOLVED_TRUE_POSITIVE
        if payload.true_positive
        else AlertStatus.RESOLVED_FALSE_POSITIVE
    )
    alert.resolved_at = datetime.now(UTC).replace(tzinfo=None)
    alert.resolved_by_id = current_user.id
    alert.resolution_note = payload.note

    _audit(
        db,
        action="alert.resolve",
        user_id=current_user.id,
        detail=(
            f"alert={alert_id} subject={alert.user_id} "
            f"verdict={'TRUE' if payload.true_positive else 'FALSE'} positive"
        ),
        request=request,
    )
    db.commit()
    db.refresh(alert)
    return alert


@router.post(
    "/{alert_id}/notes",
    response_model=AlertNoteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add an investigation note",
)
def add_note(
    alert_id: int,
    payload: AlertNoteCreate,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> AlertNote:
    """Append a note. Append-only: notes are never edited or deleted.

    An investigation record that can be silently rewritten after the fact is not a
    record, it is a draft. If an analyst was wrong at 14:00 and right at 16:00, both
    belong in the file - that is what makes it an audit trail rather than a story.
    """
    alert = db.get(Alert, alert_id)
    if alert is None:
        raise HTTPException(status_code=404, detail="No such alert.")

    note = AlertNote(alert_id=alert_id, author_id=current_user.id, body=payload.body)
    db.add(note)
    db.commit()
    db.refresh(note)
    return note
