from pydantic import BaseModel
from typing import Optional

class EmployeeSalaryRevisionCreate(BaseModel):
    name: Optional[str] = None

class EmployeeSalaryRevisionUpdate(BaseModel):
    status: Optional[str] = None

class EmployeeSalaryRevisionResponse(EmployeeSalaryRevisionCreate):
    id: str
