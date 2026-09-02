from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class LeaveTypeConfig(BaseModel):
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

class LeavePolicy(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    policyCode: str
    version: int
    name: str
    description: Optional[str] = None
    effectiveFrom: datetime
    effectiveTo: Optional[datetime] = None
    status: str = "Draft"
    leaveTypes: List[LeaveTypeConfig]
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
