from pydantic import BaseModel
from typing import Optional, Dict, Any

class AttendanceSummaryCreate(BaseModel):
    status: Optional[str] = None

class AttendanceSummaryUpdate(BaseModel):
    status: Optional[str] = None

class AttendanceSummaryResponse(AttendanceSummaryCreate):
    id: str
