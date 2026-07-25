from pydantic import BaseModel
from typing import Optional

class PayGroupCreate(BaseModel):
    name: Optional[str] = None

class PayGroupUpdate(BaseModel):
    status: Optional[str] = None

class PayGroupResponse(PayGroupCreate):
    id: str
