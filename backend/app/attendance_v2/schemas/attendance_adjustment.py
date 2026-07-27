from pydantic import BaseModel
from typing import Optional

class AttendanceAdjustmentCreate(BaseModel):
    pass

class AttendanceAdjustmentUpdate(BaseModel):
    pass

class AttendanceAdjustmentResponse(AttendanceAdjustmentCreate):
    id: str
