from pydantic import BaseModel
from typing import Optional

class DailyAttendanceCreate(BaseModel):
    name: Optional[str] = None

class DailyAttendanceUpdate(BaseModel):
    status: Optional[str] = None

class DailyAttendanceResponse(DailyAttendanceCreate):
    id: str
