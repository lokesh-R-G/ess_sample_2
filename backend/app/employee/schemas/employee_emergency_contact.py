from pydantic import BaseModel
from typing import Optional

class EmployeeEmergencyContactCreate(BaseModel):
    pass

class EmployeeEmergencyContactUpdate(BaseModel):
    pass

class EmployeeEmergencyContactResponse(EmployeeEmergencyContactCreate):
    id: str
