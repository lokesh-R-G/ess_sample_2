from pydantic import BaseModel
from typing import Optional

class LeaveApprovalWorkflowCreate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class LeaveApprovalWorkflowUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class LeaveApprovalWorkflowResponse(LeaveApprovalWorkflowCreate):
    id: str
