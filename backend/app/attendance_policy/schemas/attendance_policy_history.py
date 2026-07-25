from pydantic import BaseModel
from typing import Optional

class AttendancePolicyHistoryCreate(BaseModel):
    name: Optional[str] = None

class AttendancePolicyHistoryUpdate(BaseModel):
    status: Optional[str] = None

class AttendancePolicyHistoryResponse(AttendancePolicyHistoryCreate):
    id: str
