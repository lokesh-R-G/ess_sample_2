from pydantic import BaseModel
from typing import Optional

class NotificationTemplateCreate(BaseModel):
    pass

class NotificationTemplateUpdate(BaseModel):
    pass

class NotificationTemplateResponse(NotificationTemplateCreate):
    id: str
