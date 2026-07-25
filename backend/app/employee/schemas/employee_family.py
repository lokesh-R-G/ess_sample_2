from pydantic import BaseModel
from typing import Optional

class EmployeeFamilyCreate(BaseModel):
    employeeId: str

class EmployeeFamilyUpdate(BaseModel):
    status: Optional[str] = None

class EmployeeFamilyResponse(EmployeeFamilyCreate):
    id: str
