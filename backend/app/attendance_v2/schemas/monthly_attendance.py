from pydantic import BaseModel
from typing import Optional

class MonthlyAttendanceCreate(BaseModel):
    name: Optional[str] = None

class MonthlyAttendanceUpdate(BaseModel):
    status: Optional[str] = None

class MonthlyAttendanceResponse(MonthlyAttendanceCreate):
    id: str
