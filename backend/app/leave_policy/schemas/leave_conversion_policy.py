from pydantic import BaseModel
from typing import Optional

class LeaveConversionPolicyCreate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class LeaveConversionPolicyUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class LeaveConversionPolicyResponse(LeaveConversionPolicyCreate):
    id: str
