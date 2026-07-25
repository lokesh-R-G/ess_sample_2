from pydantic import BaseModel
from typing import Optional

class EmployeeShiftAssignmentCreate(BaseModel):
    employeeId: str

class EmployeeShiftAssignmentUpdate(BaseModel):
    status: Optional[str] = None

class EmployeeShiftAssignmentResponse(EmployeeShiftAssignmentCreate):
    id: str
