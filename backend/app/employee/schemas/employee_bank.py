from pydantic import BaseModel
from typing import Optional

class EmployeeBankCreate(BaseModel):
    employeeId: str
    bankName: Optional[str] = None
    branchName: Optional[str] = None
    accountNumber: Optional[str] = None
    ifscCode: Optional[str] = None
    accountType: Optional[str] = None
    nameAsPerBank: Optional[str] = None

class EmployeeBankUpdate(BaseModel):
    status: Optional[str] = None
    bankName: Optional[str] = None
    branchName: Optional[str] = None
    accountNumber: Optional[str] = None
    ifscCode: Optional[str] = None
    accountType: Optional[str] = None
    nameAsPerBank: Optional[str] = None

class EmployeeBankResponse(EmployeeBankCreate):
    id: str
    status: str
