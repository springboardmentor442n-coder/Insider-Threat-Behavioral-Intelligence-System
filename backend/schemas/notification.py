"""
Pydantic schemas for notifications.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class NotificationResponse(BaseModel):
    id: int
    source_type: str
    source_id: int
    notification_type: str
    title: str
    message: str
    severity: str
    event_created_at: datetime
    created_at: datetime
    read_at: Optional[datetime] = None
    is_read: bool

    model_config = ConfigDict(from_attributes=True)


class NotificationListResponse(BaseModel):
    notifications: list[NotificationResponse]
    unread_count: int


class NotificationReadResponse(BaseModel):
    id: int
    read_at: datetime
    unread_count: int


class NotificationReadAllResponse(BaseModel):
    updated_count: int
    unread_count: int
    