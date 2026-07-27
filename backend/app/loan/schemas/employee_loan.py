from pydantic import BaseModel
from typing import Optional

class EmployeeLoanCreate(BaseModel):
    pass

class EmployeeLoanUpdate(BaseModel):
    pass

class EmployeeLoanResponse(EmployeeLoanCreate):
    id: str
