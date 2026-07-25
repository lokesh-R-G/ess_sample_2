from typing import Optional, List, Dict
from datetime import datetime
from pydantic import BaseModel, Field

class PayslipModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    companyId: str
    branchId: str
    employeeId: str
    employeeCode: str
    employeeName: str
    designation: str
    department: str
    location: str
    costCenter: Optional[str] = None
    payrollRunId: str
    month: int
    year: int
    payPeriodStart: datetime
    payPeriodEnd: datetime
    generatedDate: datetime
    publishedDate: Optional[datetime] = None
    currency: str = "INR"
    status: str = "Draft"
    grossEarnings: float = 0.0
    grossDeductions: float = 0.0
    grossReimbursements: float = 0.0
    tax: float = 0.0
    netSalary: float = 0.0
    earnings: Dict[str, float] = {}
    deductions: Dict[str, float] = {}
    reimbursements: Dict[str, float] = {}
    employerContribution: Dict[str, float] = {}
    attendanceSummary: Dict[str, float] = {}
    leaveSummary: Dict[str, float] = {}
    remarks: Optional[str] = None
    version: int = 1
    pdfPath: Optional[str] = None
    checksum: Optional[str] = None
    createdBy: str
    createdAt: datetime
    updatedAt: datetime
