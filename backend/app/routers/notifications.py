"""Notification centre API. Spec Module 11.

The endpoints behind the bell icon: an operator's own notifications, the unread
count for the badge, and the two actions that matter (mark one read, mark all
read). Everything is scoped to the CURRENT user - you only ever see, and can only
ever mark, your own notifications. There is no endpoint to read someone else's.
"""
from __future__ import annotations

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.dependencies import CurrentUser
from backend.app.models import Notification

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


def _to_dict(n: Notification) -> dict:
    return {
        "id": n.id,
        "type": n.type.value,
        "title": n.title,
        "body": n.body,
        "severity": n.severity.value if n.severity else None,
        "subject_user_id": n.subject_user_id,
        "alert_id": n.alert_id,
        "is_read": n.is_read,
        "created_at": n.created_at.isoformat() if n.created_at else None,
    }


@router.get("", summary="This operator's notifications, newest first")
def list_notifications(
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
    unread_only: bool = Query(False, description="Only notifications not yet read"),
    limit: int = Query(50, ge=1, le=200),
):
    """The feed. Scoped to the current operator - never anyone else's."""
    stmt = select(Notification).where(Notification.recipient_id == current_user.id)
    if unread_only:
        stmt = stmt.where(Notification.is_read.is_(False))
    stmt = stmt.order_by(Notification.created_at.desc()).limit(limit)
    rows = db.scalars(stmt).all()
    return {"notifications": [_to_dict(n) for n in rows]}


@router.get("/unread-count", summary="Badge count")
def unread_count(
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
):
    """The number on the bell. One cheap COUNT, so it can be polled."""
    n = db.scalar(
        select(func.count())
        .select_from(Notification)
        .where(
            Notification.recipient_id == current_user.id,
            Notification.is_read.is_(False),
        )
    )
    return {"unread": int(n or 0)}


@router.post("/{notification_id}/read", summary="Mark one read")
def mark_read(
    notification_id: int,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
):
    """Mark a single notification read. 404 if it is not yours - you cannot touch
    another operator's notifications, and asking about one you do not own tells you
    nothing about whether it exists."""
    n = db.get(Notification, notification_id)
    if n is None or n.recipient_id != current_user.id:
        raise HTTPException(404, "No such notification.")
    if not n.is_read:
        n.is_read = True
        n.read_at = datetime.utcnow()
        db.commit()
    return {"id": notification_id, "is_read": True}


@router.post("/read-all", summary="Mark all read")
def mark_all_read(
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
):
    """Clear the badge: mark every unread notification for this operator read."""
    result = db.execute(
        update(Notification)
        .where(
            Notification.recipient_id == current_user.id,
            Notification.is_read.is_(False),
        )
        .values(is_read=True, read_at=datetime.utcnow())
    )
    db.commit()
    return {"marked_read": int(result.rowcount or 0)}
