from typing import Optional, Any, Dict
from datetime import datetime
from pydantic import BaseModel, Field

class ApprovalModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    employeeId: str
    reportingManagerEmployeeId: Optional[str] = None
    approvalType: str
    status: str = "PENDING"
    requestData: Dict[str, Any] = Field(default_factory=dict)
    remarks: Optional[str] = None
    
    # Audit
    createdAt: Optional[datetime] = None
    createdBy: Optional[str] = None
    approvedAt: Optional[datetime] = None
    approvedBy: Optional[str] = None
