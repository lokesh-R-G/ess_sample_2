from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class ConversationModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    type: str = "DIRECT"
    participants: List[str] = []
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)
    lastMessageAt: datetime = Field(default_factory=datetime.utcnow)

class ConversationResponse(ConversationModel):
    # Flattened for API response where _id -> id
    pass
