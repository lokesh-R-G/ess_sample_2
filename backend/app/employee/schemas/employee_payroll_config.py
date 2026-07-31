from pydantic import BaseModel
from typing import Optional, Literal

class EmployeePayrollConfigCreate(BaseModel):
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

class EmployeePayrollConfigUpdate(BaseModel):
    status: Optional[str] = None
    salaryStructureId: Optional[str] = None
    monthlyGross: Optional[float] = None
    ctc: Optional[float] = None
    pfEnabled: Optional[bool] = None
    wantsPf: Optional[bool] = None
    pfCalculationMethod: Optional[Literal["Ceiling", "Actual", "Default"]] = None
    esiEnabled: Optional[bool] = None
    workingDayMethod: Optional[Literal["Calendar Days", "Working Days", "Attendance Based", "Fixed 30 Days"]] = None
    existingPensionMember: Optional[bool] = None

class EmployeePayrollConfigResponse(EmployeePayrollConfigCreate):
    id: str
    status: str
