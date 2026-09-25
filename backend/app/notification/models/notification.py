from typing import Optional
from datetime import datetime, timezone
from pydantic import Field
from app.core.models.base_model import BaseDBModel

class NotificationModel(BaseDBModel):
    recipientEmployeeId: str
    type: str
    event: str
    title: str
    message: str
    entityType: Optional[str] = None
    entityId: Optional[str] = None
    actorEmployeeId: Optional[str] = None
    isRead: bool = False
    readAt: Optional[datetime] = None
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
