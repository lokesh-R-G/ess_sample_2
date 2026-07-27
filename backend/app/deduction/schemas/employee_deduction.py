from pydantic import BaseModel
from typing import Optional

class EmployeeDeductionCreate(BaseModel):
    pass

class EmployeeDeductionUpdate(BaseModel):
    pass

class EmployeeDeductionResponse(EmployeeDeductionCreate):
    id: str
