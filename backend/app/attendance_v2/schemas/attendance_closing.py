from pydantic import BaseModel
from typing import Optional, Dict, Any

class AttendanceClosingCreate(BaseModel):
    status: Optional[str] = None

class AttendanceClosingUpdate(BaseModel):
    status: Optional[str] = None

class AttendanceClosingResponse(AttendanceClosingCreate):
    id: str
