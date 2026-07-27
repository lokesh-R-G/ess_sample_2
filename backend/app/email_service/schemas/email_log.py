from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class EmailLogCreate(BaseModel):
    recipient: str
    subject: str
    template: str
    status: str
    sent_time: Optional[datetime] = None
    failure_reason: Optional[str] = None
    message_id: Optional[str] = None
    attachment: Optional[str] = None
    retry_count: int = 0

class EmailLogResponse(EmailLogCreate):
    id: str
