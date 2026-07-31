from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class EmploymentHistoryModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    employeeId: str
    companyId: Optional[str] = None
    branchId: Optional[str] = None
    departmentId: Optional[str] = None
    designationId: Optional[str] = None
    dateOfJoining: Optional[datetime] = None
    employmentType: Optional[str] = None
    reportingManagerId: Optional[str] = None
    shiftId: Optional[str] = None
    noticePeriodDays: int = 0
    status: str = "Active"
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    createdBy: Optional[str] = None
    updatedBy: Optional[str] = None
    deletedAt: Optional[datetime] = None
    deletedBy: Optional[str] = None
