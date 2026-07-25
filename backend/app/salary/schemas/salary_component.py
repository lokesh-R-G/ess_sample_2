from pydantic import BaseModel
from typing import Optional

class SalaryComponentCreate(BaseModel):
    name: Optional[str] = None

class SalaryComponentUpdate(BaseModel):
    status: Optional[str] = None

class SalaryComponentResponse(SalaryComponentCreate):
    id: str
