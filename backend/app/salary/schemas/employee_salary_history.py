from pydantic import BaseModel
from typing import Optional

class EmployeeSalaryHistoryCreate(BaseModel):
    name: Optional[str] = None

class EmployeeSalaryHistoryUpdate(BaseModel):
    status: Optional[str] = None

class EmployeeSalaryHistoryResponse(EmployeeSalaryHistoryCreate):
    id: str
