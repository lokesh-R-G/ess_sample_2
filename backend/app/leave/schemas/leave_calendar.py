from pydantic import BaseModel
from typing import Optional

class LeaveCalendarCreate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class LeaveCalendarUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class LeaveCalendarResponse(LeaveCalendarCreate):
    id: str
