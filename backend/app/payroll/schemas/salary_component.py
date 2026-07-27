from pydantic import BaseModel
from typing import Optional

class SalaryComponentCreate(BaseModel):
    pass

class SalaryComponentUpdate(BaseModel):
    pass

class SalaryComponentResponse(SalaryComponentCreate):
    id: str
