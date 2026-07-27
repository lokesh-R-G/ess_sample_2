from pydantic import BaseModel
from typing import Optional

class AttendanceLogCreate(BaseModel):
    pass

class AttendanceLogUpdate(BaseModel):
    pass

class AttendanceLogResponse(AttendanceLogCreate):
    id: str
