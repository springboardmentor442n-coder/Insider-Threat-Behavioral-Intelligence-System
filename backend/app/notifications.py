"""Notification & Escalation System. Spec Module 11.

Turns SECURITY EVENTS into notifications that reach the right operators, through
one or more delivery CHANNELS. The design keeps three concerns separate, on
purpose:

  1. EVENTS        - "a critical alert fired", "an alert was escalated". Raised by
                     the code where the event actually happens (alert generation,
                     the escalate endpoint).
  2. THE RECORD    - a persisted Notification row per (recipient, event). This is
                     the source of truth. It exists whether or not any external
                     channel is reachable.
  3. DELIVERY      - channels that READ the record and push it somewhere: the
                     in-app centre (always), and an optional webhook (Slack etc.).

Why separate them: a webhook that is down must not lose a notification. Because
the row is written first and delivery is best-effort on top, the in-app badge is
always correct and the webhook is a bonus, not a single point of failure.

WHO GETS NOTIFIED. A notification is addressed to security OPERATORS, not to the
CERT employees under investigation. Routing is deliberately simple and explicit
(see recipients_for): the person who owns an alert, plus managers/admins for the
things they are accountable for. No implicit "everyone" broadcasts - noise is how
a notification system gets muted and then ignored.
"""
from __future__ import annotations

import json
import logging
import os
import urllib.request
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models import (
    Alert,
    AlertSeverity,
    Notification,
    NotificationType,
    SecurityUser,
    UserRole,
)

logger = logging.getLogger(__name__)

# Which roles receive queue-wide events (escalations, new critical alerts) even
# when they do not personally own the alert. Managers and admins are accountable
# for the queue as a whole; analysts and SOC engineers are notified about what
# they own.
_OVERSIGHT_ROLES = (UserRole.SECURITY_MANAGER, UserRole.ADMINISTRATOR)

# The webhook channel is OFF unless this env var is set. That is the whole opt-in:
# no URL, no external calls, and the system still works fully in-app. Set it to a
# Slack/Teams/Discord incoming-webhook URL to turn external delivery on.
_WEBHOOK_ENV = "NOTIFY_WEBHOOK_URL"


def create_notification(
    db: Session,
    *,
    recipient_id: int,
    type: NotificationType,
    title: str,
    body: str = "",
    severity: AlertSeverity | None = None,
    subject_user_id: str | None = None,
    alert_id: int | None = None,
    deliver: bool = True,
) -> Notification:
    """Persist one notification, then best-effort deliver it to external channels.

    The row is committed FIRST. External delivery happens after and never raises
    into the caller - a failed webhook logs a warning and is dropped, because the
    persisted row already guarantees the operator will see it in-app.
    """
    n = Notification(
        recipient_id=recipient_id,
        type=type,
        title=title,
        body=body,
        severity=severity,
        subject_user_id=subject_user_id,
        alert_id=alert_id,
    )
    db.add(n)
    db.commit()
    db.refresh(n)

    if deliver:
        _deliver_external(n)

    return n


def notify_operators(
    db: Session,
    *,
    recipient_ids: Iterable[int],
    type: NotificationType,
    title: str,
    body: str = "",
    severity: AlertSeverity | None = None,
    subject_user_id: str | None = None,
    alert_id: int | None = None,
) -> int:
    """Create the same notification for several recipients. Returns the count.

    De-duplicates recipient ids so a manager who also owns the alert does not get
    two copies of one event.
    """
    seen: set[int] = set()
    made = 0
    for rid in recipient_ids:
        if rid in seen:
            continue
        seen.add(rid)
        create_notification(
            db,
            recipient_id=rid,
            type=type,
            title=title,
            body=body,
            severity=severity,
            subject_user_id=subject_user_id,
            alert_id=alert_id,
        )
        made += 1
    return made


def recipients_for_oversight(db: Session, *, include_id: int | None = None) -> list[int]:
    """The operator ids that should hear about a queue-wide event.

    Managers and admins (oversight), plus optionally a specific person (e.g. the
    analyst who owns the alert). Explicit and small - see the module docstring on
    why we never broadcast to everyone.
    """
    ids = set(
        db.scalars(
            select(SecurityUser.id).where(
                SecurityUser.role.in_(_OVERSIGHT_ROLES),
                SecurityUser.is_active.is_(True),
            )
        ).all()
    )
    if include_id is not None:
        ids.add(include_id)
    return sorted(ids)


# ---------------------------------------------------------------------------
# EVENT HELPERS - called from the places where the events actually happen.
# Each one turns a domain event into the right notifications for the right people.
# ---------------------------------------------------------------------------

def on_alert_escalated(
    db: Session, *, alert: Alert, actor_id: int
) -> int:
    """An alert was escalated. Notify oversight + whoever owns the alert, but not
    the person who did the escalating (they already know)."""
    recipients = recipients_for_oversight(
        db, include_id=alert.assigned_to_id
    )
    recipients = [r for r in recipients if r != actor_id]
    if not recipients:
        return 0
    return notify_operators(
        db,
        recipient_ids=recipients,
        type=NotificationType.ESCALATION,
        title=f"Alert escalated: {alert.user_id}",
        body=(f"A {alert.severity.value} alert for {alert.user_id} "
              f"({alert.alert_date}) was escalated and needs review."),
        severity=alert.severity,
        subject_user_id=alert.user_id,
        alert_id=alert.id,
    )


def on_investigation_opened(
    db: Session, *, alert: Alert, actor_id: int
) -> int:
    """An analyst opened an investigation. Notify oversight (not the analyst)."""
    recipients = [r for r in recipients_for_oversight(db) if r != actor_id]
    if not recipients:
        return 0
    return notify_operators(
        db,
        recipient_ids=recipients,
        type=NotificationType.INVESTIGATION,
        title=f"Investigation opened: {alert.user_id}",
        body=(f"An investigation was opened on {alert.user_id} "
              f"from a {alert.severity.value} alert ({alert.alert_date})."),
        severity=alert.severity,
        subject_user_id=alert.user_id,
        alert_id=alert.id,
    )


def notify_new_critical_alerts(
    db: Session, *, alerts: list[Alert]
) -> int:
    """After alert generation, notify oversight about NEW high/critical alerts.

    Batched into one summary notification per recipient rather than one per alert -
    a generation run that raised forty critical alerts should not fire forty
    notifications. Volume is exactly how a notification system trains its users to
    ignore it.
    """
    hot = [a for a in alerts
           if a.severity in (AlertSeverity.HIGH, AlertSeverity.CRITICAL)]
    if not hot:
        return 0

    crit = sum(1 for a in hot if a.severity == AlertSeverity.CRITICAL)
    high = len(hot) - crit
    recipients = recipients_for_oversight(db)
    if not recipients:
        return 0

    parts = []
    if crit:
        parts.append(f"{crit} critical")
    if high:
        parts.append(f"{high} high")
    summary = " and ".join(parts)

    # point the deep-link at the single most severe alert
    worst = max(hot, key=lambda a: (a.severity == AlertSeverity.CRITICAL, a.risk_score))

    return notify_operators(
        db,
        recipient_ids=recipients,
        type=NotificationType.THREAT_ALERT,
        title=f"{summary} alert{'s' if len(hot) > 1 else ''} raised",
        body=(f"The latest detection run raised {summary} "
              f"alert{'s' if len(hot) > 1 else ''}. "
              f"Highest risk: {worst.user_id} at {worst.risk_score:.0f}."),
        severity=AlertSeverity.CRITICAL if crit else AlertSeverity.HIGH,
        subject_user_id=worst.user_id,
        alert_id=worst.id,
    )


# ---------------------------------------------------------------------------
# EXTERNAL DELIVERY - the optional webhook channel. Off unless configured.
# ---------------------------------------------------------------------------

def webhook_configured() -> bool:
    return bool(os.environ.get(_WEBHOOK_ENV, "").strip())


def _deliver_external(n: Notification) -> None:
    """Best-effort push to the webhook channel, if one is configured.

    NEVER raises. A delivery failure is logged and swallowed: the notification is
    already persisted, so the operator will still see it in-app. This is the whole
    reason record and delivery are separate.
    """
    url = os.environ.get(_WEBHOOK_ENV, "").strip()
    if not url:
        return  # channel off - in-app only, which is a complete system on its own

    payload = {
        # A Slack-compatible shape ("text"), which most incoming webhooks accept.
        "text": f"[{(n.severity.value if n.severity else 'info').upper()}] "
                f"{n.title}\n{n.body}",
        "notification": {
            "type": n.type.value,
            "title": n.title,
            "body": n.body,
            "severity": n.severity.value if n.severity else None,
            "subject_user_id": n.subject_user_id,
            "alert_id": n.alert_id,
        },
    }
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        urllib.request.urlopen(req, timeout=5)  # noqa: S310 - operator-configured URL
    except Exception as e:  # noqa: BLE001 - delivery is best-effort by design
        logger.warning("Webhook delivery failed (notification %s persisted anyway): %s",
                       n.id, e)
