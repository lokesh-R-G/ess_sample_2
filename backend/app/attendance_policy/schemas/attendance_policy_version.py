from pydantic import BaseModel
from typing import Optional

class AttendancePolicyVersionCreate(BaseModel):
    name: Optional[str] = None

class AttendancePolicyVersionUpdate(BaseModel):
    status: Optional[str] = None

class AttendancePolicyVersionResponse(AttendancePolicyVersionCreate):
    id: str
