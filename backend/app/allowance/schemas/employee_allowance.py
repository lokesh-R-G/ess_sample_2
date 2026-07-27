from pydantic import BaseModel
from typing import Optional

class EmployeeAllowanceCreate(BaseModel):
    pass

class EmployeeAllowanceUpdate(BaseModel):
    pass

class EmployeeAllowanceResponse(EmployeeAllowanceCreate):
    id: str
