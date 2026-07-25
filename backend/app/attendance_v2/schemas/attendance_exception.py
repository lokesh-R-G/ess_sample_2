from pydantic import BaseModel
from typing import Optional, Dict, Any

class AttendanceExceptionCreate(BaseModel):
    status: Optional[str] = None

class AttendanceExceptionUpdate(BaseModel):
    status: Optional[str] = None

class AttendanceExceptionResponse(AttendanceExceptionCreate):
    id: str
