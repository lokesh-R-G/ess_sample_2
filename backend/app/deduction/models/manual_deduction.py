from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class ManualPayrollAdjustment(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    employeeId: str
    companyId: str
    branchId: Optional[str] = None
    payrollCycleId: Optional[str] = None
    payrollPeriod: str # YYYY-MM
    deductionType: str # "Salary Advance", "TDS", "LWF", "PT", "Other"
    amount: float
    description: Optional[str] = None
    status: str = "Active"
    version: int = 1
    isCurrent: bool = True
    originalAdjustmentId: Optional[str] = None
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)
    createdBy: Optional[str] = None
    updatedBy: Optional[str] = None
    deletedAt: Optional[datetime] = None
