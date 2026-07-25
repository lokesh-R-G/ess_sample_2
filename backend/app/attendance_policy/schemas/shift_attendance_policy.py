from pydantic import BaseModel
from typing import Optional

class ShiftAttendancePolicyCreate(BaseModel):
    name: Optional[str] = None

class ShiftAttendancePolicyUpdate(BaseModel):
    status: Optional[str] = None

class ShiftAttendancePolicyResponse(ShiftAttendancePolicyCreate):
    id: str
