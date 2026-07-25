from pydantic import BaseModel
from typing import Optional

class EmployeeDeductionProfileCreate(BaseModel):
    status: Optional[str] = "Active"

class EmployeeDeductionProfileUpdate(BaseModel):
    status: Optional[str] = None

class EmployeeDeductionProfileResponse(EmployeeDeductionProfileCreate):
    id: str
