from pydantic import BaseModel
from typing import Optional

class LeaveApprovalCreate(BaseModel):
    pass

class LeaveApprovalUpdate(BaseModel):
    pass

class LeaveApprovalResponse(LeaveApprovalCreate):
    id: str
