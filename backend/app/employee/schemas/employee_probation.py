from pydantic import BaseModel
from typing import Optional

class EmployeeProbationCreate(BaseModel):
    employeeId: str

class EmployeeProbationUpdate(BaseModel):
    status: Optional[str] = None

class EmployeeProbationResponse(EmployeeProbationCreate):
    id: str
