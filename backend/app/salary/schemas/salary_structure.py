from pydantic import BaseModel
from typing import Optional

class SalaryStructureCreate(BaseModel):
    name: Optional[str] = None

class SalaryStructureUpdate(BaseModel):
    status: Optional[str] = None

class SalaryStructureResponse(SalaryStructureCreate):
    id: str
