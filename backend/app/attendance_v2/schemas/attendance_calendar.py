from pydantic import BaseModel
from typing import Optional

class AttendanceCalendarCreate(BaseModel):
    pass

class AttendanceCalendarUpdate(BaseModel):
    pass

class AttendanceCalendarResponse(AttendanceCalendarCreate):
    id: str
