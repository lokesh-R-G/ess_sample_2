from pydantic import BaseModel
from typing import Optional

class AttendanceCreate(BaseModel):
    name: Optional[str] = None

class AttendanceUpdate(BaseModel):
    status: Optional[str] = None

class AttendanceResponse(AttendanceCreate):
    id: str
