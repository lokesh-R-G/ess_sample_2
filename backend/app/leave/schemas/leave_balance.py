from pydantic import BaseModel
from typing import Optional

class LeaveBalanceCreate(BaseModel):
    pass

class LeaveBalanceUpdate(BaseModel):
    pass

class LeaveBalanceResponse(LeaveBalanceCreate):
    id: str
