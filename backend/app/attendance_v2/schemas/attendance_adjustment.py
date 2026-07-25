from pydantic import BaseModel
from typing import Optional

class AttendanceAdjustmentCreate(BaseModel):
    name: Optional[str] = None

class AttendanceAdjustmentUpdate(BaseModel):
    status: Optional[str] = None

class AttendanceAdjustmentResponse(AttendanceAdjustmentCreate):
    id: str
