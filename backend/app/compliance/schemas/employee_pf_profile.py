from pydantic import BaseModel
from typing import Optional

class EmployeePfProfileCreate(BaseModel):
    pass

class EmployeePfProfileUpdate(BaseModel):
    pass

class EmployeePfProfileResponse(EmployeePfProfileCreate):
    id: str
