from pydantic import BaseModel
from typing import Optional

class EmployeeEducationCreate(BaseModel):
    pass

class EmployeeEducationUpdate(BaseModel):
    pass

class EmployeeEducationResponse(EmployeeEducationCreate):
    id: str
