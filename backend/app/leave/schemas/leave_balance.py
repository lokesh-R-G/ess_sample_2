from pydantic import BaseModel
from typing import Optional

class LeaveBalanceCreate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class LeaveBalanceUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class LeaveBalanceResponse(LeaveBalanceCreate):
    id: str
