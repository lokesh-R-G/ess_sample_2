from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Literal

class EmployeePayrollConfigModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    employeeId: str
    salaryStructureId: Optional[str] = None
    monthlyGross: float = 0.0
    ctc: float = 0.0
    pfEnabled: bool = True
    wantsPf: bool = True
    pfCalculationMethod: Literal["Ceiling", "Actual", "Default"] = "Default"
    esiEnabled: bool = True
    workingDayMethod: Literal["Calendar Days", "Working Days", "Attendance Based", "Fixed 30 Days"] = "Calendar Days"
    existingPensionMember: bool = False
    ptState: Optional[str] = None
    status: str = "Active"
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    createdBy: Optional[str] = None
    updatedBy: Optional[str] = None
    deletedAt: Optional[datetime] = None
    deletedBy: Optional[str] = None
