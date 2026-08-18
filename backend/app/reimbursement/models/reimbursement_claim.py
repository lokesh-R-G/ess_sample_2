from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class ReimbursementClaimModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    employeeId: str
    companyId: str
    branchId: str
    claimType: str  # "TripSheet", "CashVoucher", etc.
    description: str
    
    status: str = "DRAFT"  # DRAFT, SUBMITTED, HOD_REVIEW, HOD_REJECTED, HOD_APPROVED, ACCOUNTS_REVIEW, ACCOUNTS_REJECTED, ACCOUNTS_APPROVED, PAYROLL_ELIGIBLE, PAYROLL_INCLUDED
    
    calculatedAmount: float = 0.0
    approvedAmount: float = 0.0
    
    # HOD Approval
    hodStatus: Optional[str] = None
    hodId: Optional[str] = None
    hodActionAt: Optional[datetime] = None
    hodRejectionReason: Optional[str] = None
    
    # Accounts Approval
    accountsStatus: Optional[str] = None
    accountsId: Optional[str] = None
    accountsActionAt: Optional[datetime] = None
    accountsRejectionReason: Optional[str] = None

    # Attachments
    attachmentIds: list[str] = Field(default_factory=list)
    
    # Payroll Integration
    payrollCycleId: Optional[str] = None
    payrollStatus: Optional[str] = None
    payrollLineItemId: Optional[str] = None
    
    # Audit
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    createdBy: Optional[str] = None
    updatedBy: Optional[str] = None
    deletedAt: Optional[datetime] = None
