from pydantic import BaseModel
from typing import Optional

class LeaveQuotaPolicyCreate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class LeaveQuotaPolicyUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class LeaveQuotaPolicyResponse(LeaveQuotaPolicyCreate):
    id: str
