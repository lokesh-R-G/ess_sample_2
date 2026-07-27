from pydantic import BaseModel
from typing import Optional

class NotificationCreate(BaseModel):
    pass

class NotificationUpdate(BaseModel):
    pass

class NotificationResponse(NotificationCreate):
    id: str
