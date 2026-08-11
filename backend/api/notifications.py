"""
Notification API routes.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database.session import get_db
from backend.schemas.notification import (
    NotificationListResponse,
    NotificationReadAllResponse,
    NotificationReadResponse,
)
from backend.services.notification_service import (
    get_notifications,
    get_unread_count,
    mark_all_notifications_read,
    mark_notification_read,
)
from backend.utils.security import get_current_user


router = APIRouter()


@router.get(
    "/",
    response_model=NotificationListResponse,
)
def list_notifications(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    notifications, unread_count = get_notifications(
        db,
        user.id,
    )

    response = []

    for notification in notifications:
        response.append(
            {
                "id": notification.id,
                "source_type": notification.source_type,
                "source_id": notification.source_id,
                "notification_type": notification.notification_type,
                "title": notification.title,
                "message": notification.message,
                "severity": notification.severity,
                "event_created_at": notification.event_created_at,
                "created_at": notification.created_at,
                "read_at": notification.read_at,
                "is_read": notification.read_at is not None,
            }
        )

    return {
        "notifications": response,
        "unread_count": unread_count,
    }


@router.get(
    "/unread-count",
)
def unread_count(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return {
        "unread_count": get_unread_count(
            db,
            user.id,
        )
    }


@router.patch(
    "/{notification_id}/read",
    response_model=NotificationReadResponse,
)
def read_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    notification = mark_notification_read(
        db,
        user.id,
        notification_id,
    )

    if notification is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found.",
        )

    return {
        "id": notification.id,
        "read_at": notification.read_at,
        "unread_count": get_unread_count(
            db,
            user.id,
        ),
    }


@router.post(
    "/read-all",
    response_model=NotificationReadAllResponse,
)
def read_all_notifications(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    updated_count = mark_all_notifications_read(
        db,
        user.id,
    )

    return {
        "updated_count": updated_count,
        "unread_count": 0,
    }
