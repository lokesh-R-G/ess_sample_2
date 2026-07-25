from pydantic import BaseModel
from typing import Optional

class LeaveEncashmentCreate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class LeaveEncashmentUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class LeaveEncashmentResponse(LeaveEncashmentCreate):
    id: str
