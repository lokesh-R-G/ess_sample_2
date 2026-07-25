from pydantic import BaseModel
from typing import Optional

class AttendanceHistoryCreate(BaseModel):
    name: Optional[str] = None

class AttendanceHistoryUpdate(BaseModel):
    status: Optional[str] = None

class AttendanceHistoryResponse(AttendanceHistoryCreate):
    id: str
