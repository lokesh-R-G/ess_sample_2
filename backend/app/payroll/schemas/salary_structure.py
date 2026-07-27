from pydantic import BaseModel
from typing import Optional

class SalaryStructureCreate(BaseModel):
    pass

class SalaryStructureUpdate(BaseModel):
    pass

class SalaryStructureResponse(SalaryStructureCreate):
    id: str
