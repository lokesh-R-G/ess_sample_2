from pydantic import BaseModel
from typing import Optional, Dict, Any

class AttendanceReplayQueueCreate(BaseModel):
    status: Optional[str] = None

class AttendanceReplayQueueUpdate(BaseModel):
    status: Optional[str] = None

class AttendanceReplayQueueResponse(AttendanceReplayQueueCreate):
    id: str
