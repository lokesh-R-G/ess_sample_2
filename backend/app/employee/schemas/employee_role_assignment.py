from pydantic import BaseModel
from typing import Optional

class EmployeeRoleAssignmentCreate(BaseModel):
    employeeId: str

class EmployeeRoleAssignmentUpdate(BaseModel):
    status: Optional[str] = None

class EmployeeRoleAssignmentResponse(EmployeeRoleAssignmentCreate):
    id: str
