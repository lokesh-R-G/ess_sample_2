from typing import Optional, Any, Dict
from datetime import datetime
from pydantic import BaseModel

class ApprovalSubmit(BaseModel):
    employeeId: str
    reportingManagerEmployeeId: Optional[str] = None
    approvalType: str
    requestData: Dict[str, Any] = {}
    remarks: Optional[str] = None

class ApprovalAction(BaseModel):
    action: str  # APPROVE, REJECT, WITHDRAW, CANCEL
    remarks: Optional[str] = None
    actedBy: str

class ApprovalResponse(BaseModel):
    id: str
    employeeId: str
    employeeCode: Optional[str] = None
    employeeName: Optional[str] = None
    reportingManagerEmployeeId: Optional[str] = None
    approvalType: str
    status: str
    requestData: Dict[str, Any]
    remarks: Optional[str] = None
    createdAt: Optional[datetime] = None
    approvedAt: Optional[datetime] = None
    approvedBy: Optional[str] = None
