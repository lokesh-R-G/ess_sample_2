from pydantic import BaseModel
from typing import Optional

class EmployeeFamilyCreate(BaseModel):
    pass

class EmployeeFamilyUpdate(BaseModel):
    pass

class EmployeeFamilyResponse(EmployeeFamilyCreate):
    id: str
