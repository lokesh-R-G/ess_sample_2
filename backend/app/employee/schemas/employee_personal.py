from pydantic import BaseModel
from typing import Optional

class EmployeePersonalCreate(BaseModel):
    employeeId: str

class EmployeePersonalUpdate(BaseModel):
    status: Optional[str] = None

class EmployeePersonalResponse(EmployeePersonalCreate):
    id: str
