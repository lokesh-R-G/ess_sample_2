from pydantic import BaseModel
from typing import Optional

class EmployeeContactCreate(BaseModel):
    employeeId: str
    officialEmail: Optional[str] = None
    officialMobile: Optional[str] = None
    personalEmail: Optional[str] = None
    personalMobile: Optional[str] = None
    emergencyContactName: Optional[str] = None
    emergencyContactNumber: Optional[str] = None
    emergencyContactRelation: Optional[str] = None

class EmployeeContactUpdate(BaseModel):
    status: Optional[str] = None
    officialEmail: Optional[str] = None
    officialMobile: Optional[str] = None
    personalEmail: Optional[str] = None
    personalMobile: Optional[str] = None
    emergencyContactName: Optional[str] = None
    emergencyContactNumber: Optional[str] = None
    emergencyContactRelation: Optional[str] = None

class EmployeeContactResponse(EmployeeContactCreate):
    id: str
    status: str
