from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class EmployeePersonalCreate(BaseModel):
    employeeId: str
    firstName: str = ""
    lastName: str = ""
    displayName: Optional[str] = None
    middleName: Optional[str] = None
    dob: Optional[datetime] = None
    gender: Optional[str] = None
    maritalStatus: Optional[str] = None
    bloodGroup: Optional[str] = None
    nationality: Optional[str] = None
    religion: Optional[str] = None

class EmployeePersonalUpdate(BaseModel):
    status: Optional[str] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    displayName: Optional[str] = None
    middleName: Optional[str] = None
    dob: Optional[datetime] = None
    gender: Optional[str] = None
    maritalStatus: Optional[str] = None
    bloodGroup: Optional[str] = None
    nationality: Optional[str] = None
    religion: Optional[str] = None

class EmployeePersonalResponse(EmployeePersonalCreate):
    id: str
    status: str
