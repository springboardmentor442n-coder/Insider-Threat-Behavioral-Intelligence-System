"""
Notification business logic.

The notification system derives notifications from existing security
records instead of inventing independent security events.

Important behavior:
- Existing records are established as read on first synchronization.
- New records become unread.
- Notifications are isolated per authenticated user.
"""

from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from backend.database.models import (
    Activity,
    Report,
    Risk,
    Threat,
)
from backend.database.notification_model import Notification


def _create_notification_if_missing(
    db: Session,
    *,
    user_id: int,
    source_type: str,
    source_id: int,
    notification_type: str,
    title: str,
    message: str,
    severity: str,
    event_created_at: datetime,
    initial_read: bool,
) -> Notification | None:
    existing = db.scalar(
        select(Notification).where(
            Notification.user_id == user_id,
            Notification.source_type == source_type,
            Notification.source_id == source_id,
        )
    )

    if existing:
        return existing

    notification = Notification(
        user_id=user_id,
        source_type=source_type,
        source_id=source_id,
        notification_type=notification_type,
        title=title,
        message=message,
        severity=severity,
        event_created_at=event_created_at,
        read_at=(
            datetime.utcnow()
            if initial_read
            else None
        ),
    )

    db.add(notification)

    return notification


def synchronize_notifications(
    db: Session,
    user_id: int,
) -> None:
    """
    Synchronize existing security records into the user's notification
    history.

    The first synchronization establishes currently existing records
    as read. Records created after that point are unread.
    """

    has_existing_notifications = db.scalar(
        select(Notification.id)
        .where(Notification.user_id == user_id)
        .limit(1)
    ) is not None

    # ------------------------------------------------------------
    # Threat notifications
    # ------------------------------------------------------------

    threats = db.scalars(
        select(Threat).order_by(
            Threat.created_at.desc()
        )
    ).all()

    for threat in threats:
        # We only surface meaningful security events.
        if threat.severity.lower() not in {
            "high",
            "critical",
            "medium",
        }:
            continue

        _create_notification_if_missing(
            db,
            user_id=user_id,
            source_type="threat",
            source_id=threat.id,
            notification_type="threat",
            title=(
                f"{threat.severity.title()} Threat Detected"
            ),
            message=(
                f"{threat.employee_name} — "
                f"{threat.threat_type}. "
                f"Risk score: {threat.risk_score:.1f}."
            ),
            severity=threat.severity.lower(),
            event_created_at=threat.created_at,
            initial_read=not has_existing_notifications,
        )

    # ------------------------------------------------------------
    # Risk notifications
    # ------------------------------------------------------------

    risks = db.scalars(
        select(Risk).order_by(
            Risk.created_at.desc()
        )
    ).all()

    for risk in risks:
        if risk.prediction.lower() not in {
            "high",
            "critical",
            "malicious",
            "anomalous",
        }:
            continue

        _create_notification_if_missing(
            db,
            user_id=user_id,
            source_type="risk",
            source_id=risk.id,
            notification_type="risk",
            title="High-Risk Assessment Updated",
            message=(
                f"Employee risk assessment returned "
                f"{risk.prediction} with score "
                f"{risk.score:.1f} using {risk.model_name}."
            ),
            severity="high",
            event_created_at=risk.created_at,
            initial_read=not has_existing_notifications,
        )

    # ------------------------------------------------------------
    # Report notifications
    # ------------------------------------------------------------

    reports = db.scalars(
        select(Report).order_by(
            Report.generated_at.desc()
        )
    ).all()

    for report in reports:
        _create_notification_if_missing(
            db,
            user_id=user_id,
            source_type="report",
            source_id=report.id,
            notification_type="report",
            title="Security Report Generated",
            message=(
                f"{report.report_name} "
                f"({report.report_type}) is available."
            ),
            severity="info",
            event_created_at=report.generated_at,
            initial_read=not has_existing_notifications,
        )

    # ------------------------------------------------------------
    # Activity notifications
    # ------------------------------------------------------------

    activities = db.scalars(
        select(Activity).order_by(
            Activity.timestamp.desc()
        )
    ).all()

    for activity in activities:
        if activity.severity.lower() not in {
            "high",
            "critical",
        }:
            continue

        _create_notification_if_missing(
            db,
            user_id=user_id,
            source_type="activity",
            source_id=activity.id,
            notification_type="activity",
            title="High-Severity Activity Detected",
            message=activity.description,
            severity=activity.severity.lower(),
            event_created_at=activity.timestamp,
            initial_read=not has_existing_notifications,
        )

    db.commit()


def get_notifications(
    db: Session,
    user_id: int,
) -> tuple[list[Notification], int]:
    """
    Synchronize and return notifications for a user.
    """

    synchronize_notifications(
        db,
        user_id,
    )

    notifications = db.scalars(
        select(Notification)
        .where(Notification.user_id == user_id)
        .order_by(
            Notification.event_created_at.desc()
        )
    ).all()

    unread_count = db.scalar(
        select(func.count(Notification.id))
        .where(
            Notification.user_id == user_id,
            Notification.read_at.is_(None),
        )
    ) or 0

    return notifications, unread_count


def mark_notification_read(
    db: Session,
    user_id: int,
    notification_id: int,
) -> Notification | None:
    notification = db.scalar(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == user_id,
        )
    )

    if notification is None:
        return None

    if notification.read_at is None:
        notification.read_at = datetime.utcnow()
        db.commit()
        db.refresh(notification)

    return notification


def mark_all_notifications_read(
    db: Session,
    user_id: int,
) -> int:
    notifications = db.scalars(
        select(Notification).where(
            Notification.user_id == user_id,
            Notification.read_at.is_(None),
        )
    ).all()

    now = datetime.utcnow()

    for notification in notifications:
        notification.read_at = now

    db.commit()

    return len(notifications)


def get_unread_count(
    db: Session,
    user_id: int,
) -> int:
    return (
        db.scalar(
            select(func.count(Notification.id))
            .where(
                Notification.user_id == user_id,
                Notification.read_at.is_(None),
            )
        )
        or 0
    )
