from pydantic import BaseModel
from typing import Optional

class EmployeeSalaryComponentCreate(BaseModel):
    name: Optional[str] = None

class EmployeeSalaryComponentUpdate(BaseModel):
    status: Optional[str] = None

class EmployeeSalaryComponentResponse(EmployeeSalaryComponentCreate):
    id: str
