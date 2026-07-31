from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class EmploymentHistoryCreate(BaseModel):
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

class EmploymentHistoryUpdate(BaseModel):
    status: Optional[str] = None
    companyId: Optional[str] = None
    branchId: Optional[str] = None
    departmentId: Optional[str] = None
    designationId: Optional[str] = None
    dateOfJoining: Optional[datetime] = None
    employmentType: Optional[str] = None
    reportingManagerId: Optional[str] = None
    shiftId: Optional[str] = None
    noticePeriodDays: Optional[int] = None

class EmploymentHistoryResponse(EmploymentHistoryCreate):
    id: str
    status: str
    # Enriched objects for frontend
    company: Optional[dict] = None
    branch: Optional[dict] = None
    department: Optional[dict] = None
    designation: Optional[dict] = None
