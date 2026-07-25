from pydantic import BaseModel
from typing import Optional

class EmployeeConfirmationCreate(BaseModel):
    employeeId: str

class EmployeeConfirmationUpdate(BaseModel):
    status: Optional[str] = None

class EmployeeConfirmationResponse(EmployeeConfirmationCreate):
    id: str
