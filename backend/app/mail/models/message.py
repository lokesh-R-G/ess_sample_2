from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class MessageModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    clientMessageId: str  # For idempotency
    conversationId: str
    senderEmployeeId: str
    receiverEmployeeId: str
    subject: Optional[str] = None
    body: str
    status: str = "SENT" # SENT, DELIVERED, READ
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    deliveredAt: Optional[datetime] = None
    readAt: Optional[datetime] = None
