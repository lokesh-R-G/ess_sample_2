from pydantic import BaseModel
from typing import Optional

class EmployeeEducationCreate(BaseModel):
    employeeId: str

class EmployeeEducationUpdate(BaseModel):
    status: Optional[str] = None

class EmployeeEducationResponse(EmployeeEducationCreate):
    id: str
