from pydantic import BaseModel
from typing import Optional

class EmployeeSalaryCreate(BaseModel):
    name: Optional[str] = None

class EmployeeSalaryUpdate(BaseModel):
    status: Optional[str] = None

class EmployeeSalaryResponse(EmployeeSalaryCreate):
    id: str
