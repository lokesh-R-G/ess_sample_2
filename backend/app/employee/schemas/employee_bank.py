from pydantic import BaseModel
from typing import Optional

class EmployeeBankCreate(BaseModel):
    employeeId: str

class EmployeeBankUpdate(BaseModel):
    status: Optional[str] = None

class EmployeeBankResponse(EmployeeBankCreate):
    id: str
