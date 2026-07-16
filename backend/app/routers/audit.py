"""The audit log endpoint - the administrator's record of who did what.

Every state-changing action an operator takes (acknowledging an alert, resolving one,
changing a role) writes an AuditLog row. This endpoint reads them back. It is the
"audit reports" the admin dashboard in Module 10 asks for.

ADMINISTRATOR ONLY. The audit log records the actions of the security team itself -
who resolved which alert, who changed whose role. That is exactly the information an
insider on the security team would want to see to cover their tracks, so it is gated
to administrators alone, one level above the managers who can action alerts.
"""

from __future__ import annotations

from typing import Annotated

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, Query

from backend.app.dependencies import CurrentUser, get_db, require_roles
from backend.app.models import AuditLog, SecurityUser, UserRole

router = APIRouter(
    prefix="/api/audit",
    tags=["audit"],
    # The whole router is admin-only. Not a per-endpoint decorator, because there is
    # no version of "read the audit log" that a non-admin should reach.
    dependencies=[Depends(require_roles(UserRole.ADMINISTRATOR))],
)


@router.get("", summary="The audit trail (administrator only)")
def list_audit_log(
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
    action: Annotated[str | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> dict:
    """Audit rows, newest first, with the operator who performed each action.

    Joined to security_users so the response carries the actor's email and name
    rather than a bare numeric id that means nothing to the person reading the log.
    The join is a LEFT join: a row whose operator has since been deleted still
    appears, because "an action by an account that no longer exists" is precisely the
    kind of thing an audit log exists to preserve.
    """
    # Total (respecting the action filter) so the frontend can paginate.
    count_stmt = select(func.count()).select_from(AuditLog)
    if action:
        count_stmt = count_stmt.where(AuditLog.action == action)
    total = db.scalar(count_stmt) or 0

    stmt = (
        select(AuditLog, SecurityUser.email, SecurityUser.full_name)
        .outerjoin(SecurityUser, SecurityUser.id == AuditLog.security_user_id)
        .order_by(desc(AuditLog.timestamp))
        .limit(limit)
        .offset(offset)
    )
    if action:
        stmt = stmt.where(AuditLog.action == action)

    rows = db.execute(stmt).all()

    entries = []
    for log, email, full_name in rows:
        entries.append(
            {
                "id": log.id,
                "action": log.action,
                "detail": log.detail,
                "ip_address": log.ip_address,
                "timestamp": log.timestamp.isoformat() if log.timestamp else None,
                "actor_id": log.security_user_id,
                "actor_email": email,
                "actor_name": full_name,
            }
        )

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "entries": entries,
    }


@router.get("/actions", summary="Distinct audit action types (administrator only)")
def audit_action_types(
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    """The set of action names in the log, for the dashboard's filter dropdown.

    Cheaper and more honest than hardcoding the list in the frontend: if a new kind
    of audited action is added to the backend, it appears here automatically rather
    than silently missing from the filter.
    """
    rows = db.execute(
        select(AuditLog.action, func.count())
        .group_by(AuditLog.action)
        .order_by(desc(func.count()))
    ).all()
    return {"actions": [{"action": a, "count": n} for a, n in rows]}