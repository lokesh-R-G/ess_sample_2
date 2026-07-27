from pydantic import BaseModel
from typing import Optional

class EmployeeCtcCreate(BaseModel):
    pass

class EmployeeCtcUpdate(BaseModel):
    pass

class EmployeeCtcResponse(EmployeeCtcCreate):
    id: str
