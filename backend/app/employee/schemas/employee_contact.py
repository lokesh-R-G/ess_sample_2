from pydantic import BaseModel
from typing import Optional

class EmployeeContactCreate(BaseModel):
    employeeId: str

class EmployeeContactUpdate(BaseModel):
    status: Optional[str] = None

class EmployeeContactResponse(EmployeeContactCreate):
    id: str
