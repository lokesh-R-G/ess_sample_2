from pydantic import BaseModel
from typing import Optional

class EmployeeCreate(BaseModel):
    employeeId: str

class EmployeeUpdate(BaseModel):
    status: Optional[str] = None

class EmployeeResponse(EmployeeCreate):
    id: str
