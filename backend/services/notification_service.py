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


from backend.services.threat_service import get_all_threats
from backend.services.investigation_service import get_all_cases
from backend.utils.cert_date_helper import get_cert_date_for_user


def synchronize_notifications(
    db: Session,
    user_id: int,
) -> None:
    """
    Synchronize live ML threat detection events and active investigation cases
    into the user's notification history.
    """

    has_existing_notifications = db.scalar(
        select(Notification.id)
        .where(Notification.user_id == user_id)
        .limit(1)
    ) is not None

    # 1. Sync Live ML Threats
    threats = get_all_threats()
    for idx, threat in enumerate(threats[:15]):
        user = str(threat.get("user") or threat.get("employee_name") or f"EMP-{idx}")
        score = float(threat.get("risk_score") or 0.0)
        severity = str(threat.get("severity") or "High").lower()
        susp_count = int(threat.get("suspicious_count") or 0)
        cert_date_str = str(threat.get("created_at") or get_cert_date_for_user(user))

        try:
            event_dt = datetime.strptime(cert_date_str[:10], "%Y-%m-%d")
        except Exception:
            event_dt = datetime(2011, 5, 16)

        _create_notification_if_missing(
            db,
            user_id=user_id,
            source_type="threat",
            source_id=1000 + idx,
            notification_type="threat",
            title=f"{severity.title()} Threat Alert: Employee {user}",
            message=f"Employee {user} flagged by {susp_count}/7 ML models with weighted risk score {score:.1f}/100.",
            severity=severity,
            event_created_at=event_dt,
            initial_read=not has_existing_notifications,
        )

    # 2. Sync Live Investigation Cases
    cases = get_all_cases()
    for idx, case in enumerate(cases[:10]):
        case_id = str(case.get("id") or f"CASE-{idx}")
        emp = str(case.get("employee") or "")
        status = str(case.get("status") or "Open")
        assigned = str(case.get("assigned_to") or "SOC Team")
        c_date_str = str(case.get("created_at") or "2011-05-16")

        try:
            event_dt = datetime.strptime(c_date_str[:10], "%Y-%m-%d")
        except Exception:
            event_dt = datetime(2011, 5, 16)

        _create_notification_if_missing(
            db,
            user_id=user_id,
            source_type="activity",
            source_id=2000 + idx,
            notification_type="activity",
            title=f"Investigation Active: {case_id}",
            message=f"Case {case_id} for {emp} is currently {status} (Assigned: {assigned}).",
            severity="medium" if status != "Open" else "high",
            event_created_at=event_dt,
            initial_read=not has_existing_notifications,
        )

    db.commit()


def get_notifications(
    db: Session,
    user_id: int,
) -> tuple[list[Notification], int]:
    """
    Synchronize and return notifications for a user.
    Purges any stale non-CERT legacy notifications.
    """
    try:
        db.query(Notification).filter(
            ~Notification.message.contains("AJF0370") &
            ~Notification.message.contains("BAL0044") &
            ~Notification.message.contains("EIS0041") &
            ~Notification.message.contains("IBB0359") &
            ~Notification.message.contains("HDS0367") &
            ~Notification.message.contains("OBH0499") &
            ~Notification.message.contains("CASE-") &
            ~Notification.title.contains("Threat Alert") &
            ~Notification.title.contains("Investigation")
        ).delete(synchronize_session=False)
        db.commit()
    except Exception:
        pass

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
