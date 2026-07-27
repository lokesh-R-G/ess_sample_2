from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class EmailLogModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    recipient: str
    subject: str
    template: str
    status: str
    sent_time: Optional[datetime] = None
    failure_reason: Optional[str] = None
    message_id: Optional[str] = None
    attachment: Optional[str] = None
    retry_count: int = 0
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    createdBy: Optional[str] = None
    updatedBy: Optional[str] = None
    deletedAt: Optional[datetime] = None
    deletedBy: Optional[str] = None
