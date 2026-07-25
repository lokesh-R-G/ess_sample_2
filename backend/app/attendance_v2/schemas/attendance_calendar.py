from pydantic import BaseModel
from typing import Optional, Dict, Any

class AttendanceCalendarCreate(BaseModel):
    status: Optional[str] = None

class AttendanceCalendarUpdate(BaseModel):
    status: Optional[str] = None

class AttendanceCalendarResponse(AttendanceCalendarCreate):
    id: str
