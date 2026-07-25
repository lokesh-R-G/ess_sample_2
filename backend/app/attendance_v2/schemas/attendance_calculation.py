from pydantic import BaseModel
from typing import Optional

class AttendanceCalculationCreate(BaseModel):
    name: Optional[str] = None

class AttendanceCalculationUpdate(BaseModel):
    status: Optional[str] = None

class AttendanceCalculationResponse(AttendanceCalculationCreate):
    id: str
