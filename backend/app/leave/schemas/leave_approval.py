from pydantic import BaseModel
from typing import Optional

class LeaveApprovalCreate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class LeaveApprovalUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class LeaveApprovalResponse(LeaveApprovalCreate):
    id: str
