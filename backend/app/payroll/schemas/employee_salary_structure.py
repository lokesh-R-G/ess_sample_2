from pydantic import BaseModel
from typing import Optional

class EmployeeSalaryStructureCreate(BaseModel):
    pass

class EmployeeSalaryStructureUpdate(BaseModel):
    pass

class EmployeeSalaryStructureResponse(EmployeeSalaryStructureCreate):
    id: str
