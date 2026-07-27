from pydantic import BaseModel
from typing import Optional

class AttendancePolicyCreate(BaseModel):
    pass

class AttendancePolicyUpdate(BaseModel):
    pass

class AttendancePolicyResponse(AttendancePolicyCreate):
    id: str
