from pydantic import BaseModel
from typing import Optional

class LeaveTypeCreate(BaseModel):
    pass

class LeaveTypeUpdate(BaseModel):
    pass

class LeaveTypeResponse(LeaveTypeCreate):
    id: str
