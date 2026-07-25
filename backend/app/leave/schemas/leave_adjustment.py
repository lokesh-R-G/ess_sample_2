from pydantic import BaseModel
from typing import Optional

class LeaveAdjustmentCreate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class LeaveAdjustmentUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class LeaveAdjustmentResponse(LeaveAdjustmentCreate):
    id: str
