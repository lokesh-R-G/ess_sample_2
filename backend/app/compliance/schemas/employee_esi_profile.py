from pydantic import BaseModel
from typing import Optional

class EmployeeEsiProfileCreate(BaseModel):
    pass

class EmployeeEsiProfileUpdate(BaseModel):
    pass

class EmployeeEsiProfileResponse(EmployeeEsiProfileCreate):
    id: str
