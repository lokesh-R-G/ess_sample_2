from pydantic import BaseModel
from typing import Optional

class EmployeeAddressCreate(BaseModel):
    employeeId: str

class EmployeeAddressUpdate(BaseModel):
    status: Optional[str] = None

class EmployeeAddressResponse(EmployeeAddressCreate):
    id: str
