from pydantic import BaseModel
from typing import Optional

class EmployeeGovernmentIdCreate(BaseModel):
    employeeId: str
    panNumber: Optional[str] = None
    aadharNumber: Optional[str] = None
    uanNumber: Optional[str] = None
    pfNumber: Optional[str] = None
    esiNumber: Optional[str] = None
    passportNumber: Optional[str] = None

class EmployeeGovernmentIdUpdate(BaseModel):
    status: Optional[str] = None
    panNumber: Optional[str] = None
    aadharNumber: Optional[str] = None
    uanNumber: Optional[str] = None
    pfNumber: Optional[str] = None
    esiNumber: Optional[str] = None
    passportNumber: Optional[str] = None

class EmployeeGovernmentIdResponse(EmployeeGovernmentIdCreate):
    id: str
    status: str
