from pydantic import BaseModel
from typing import Optional

class SalaryComponentGroupCreate(BaseModel):
    pass

class SalaryComponentGroupUpdate(BaseModel):
    pass

class SalaryComponentGroupResponse(SalaryComponentGroupCreate):
    id: str
