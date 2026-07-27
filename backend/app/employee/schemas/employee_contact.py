from pydantic import BaseModel
from typing import Optional

class EmployeeContactCreate(BaseModel):
    pass

class EmployeeContactUpdate(BaseModel):
    pass

class EmployeeContactResponse(EmployeeContactCreate):
    id: str
