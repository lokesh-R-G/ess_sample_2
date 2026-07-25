from pydantic import BaseModel
from typing import Optional

class LeaveTypeCreate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class LeaveTypeUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class LeaveTypeResponse(LeaveTypeCreate):
    id: str
