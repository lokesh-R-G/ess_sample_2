from pydantic import BaseModel
from typing import Optional

class NotificationDeliveryLogCreate(BaseModel):
    pass

class NotificationDeliveryLogUpdate(BaseModel):
    pass

class NotificationDeliveryLogResponse(NotificationDeliveryLogCreate):
    id: str
