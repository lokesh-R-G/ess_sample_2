from pydantic import BaseModel
from typing import Optional

class AttendanceLogCreate(BaseModel):
    name: Optional[str] = None

class AttendanceLogUpdate(BaseModel):
    status: Optional[str] = None

class AttendanceLogResponse(AttendanceLogCreate):
    id: str
