from pydantic import BaseModel
from typing import Optional

class AttendancePolicyCreate(BaseModel):
    name: Optional[str] = None

class AttendancePolicyUpdate(BaseModel):
    status: Optional[str] = None

class AttendancePolicyResponse(AttendancePolicyCreate):
    id: str
