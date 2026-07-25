from pydantic import BaseModel
from typing import Optional

class LeaveApplicationCreate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class LeaveApplicationUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class LeaveApplicationResponse(LeaveApplicationCreate):
    id: str
