from pydantic import BaseModel
from typing import Optional

class EmployeeEmergencyContactCreate(BaseModel):
    employeeId: str

class EmployeeEmergencyContactUpdate(BaseModel):
    status: Optional[str] = None

class EmployeeEmergencyContactResponse(EmployeeEmergencyContactCreate):
    id: str
