from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class LeaveTypeConfigSchema(BaseModel):
    code: str
    name: str
    enabled: bool = True
    annualEntitlement: float
    carryForwardEnabled: bool = False
    carryForwardLimit: float = 0.0
    carryForwardType: str = "FLAT"
    expiryEnabled: bool = True
    expiryRule: str = "YEAR_END"
    joiningYearProrationEnabled: bool = True
    prorationRule: str = "MONTHLY_REDUCTION"
    anniversaryEligibilityEnabled: bool = True
    zeroBalanceApprovalAllowed: bool = True
    lopEnabled: bool = True

class LeavePolicyCreate(BaseModel):
    policyCode: str
    name: str
    description: Optional[str] = None
    effectiveFrom: datetime
    leaveTypes: List[LeaveTypeConfigSchema]

class LeavePolicyResponse(BaseModel):
    id: str
    policyCode: str
    version: int
    name: str
    description: Optional[str]
    effectiveFrom: datetime
    effectiveTo: Optional[datetime]
    status: str
    leaveTypes: List[LeaveTypeConfigSchema]
    createdAt: Optional[datetime]
    updatedAt: Optional[datetime]

