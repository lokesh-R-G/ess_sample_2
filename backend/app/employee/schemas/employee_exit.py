from pydantic import BaseModel
from typing import Optional

class EmployeeExitCreate(BaseModel):
    employeeId: str

class EmployeeExitUpdate(BaseModel):
    status: Optional[str] = None

class EmployeeExitResponse(EmployeeExitCreate):
    id: str
