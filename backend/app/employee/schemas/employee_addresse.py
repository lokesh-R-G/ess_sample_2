from pydantic import BaseModel
from typing import Optional

class EmployeeAddresseCreate(BaseModel):
    pass

class EmployeeAddresseUpdate(BaseModel):
    pass

class EmployeeAddresseResponse(EmployeeAddresseCreate):
    id: str
