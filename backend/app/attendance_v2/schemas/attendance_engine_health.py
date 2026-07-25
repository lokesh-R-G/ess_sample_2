from pydantic import BaseModel
from typing import Optional, Dict, Any

class AttendanceEngineHealthCreate(BaseModel):
    status: Optional[str] = None

class AttendanceEngineHealthUpdate(BaseModel):
    status: Optional[str] = None

class AttendanceEngineHealthResponse(AttendanceEngineHealthCreate):
    id: str
