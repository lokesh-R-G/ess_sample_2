from pydantic import BaseModel
from typing import Optional

class SalaryStructureCreate(BaseModel):
    companyId: str
    name: str
    description: Optional[str] = None

class SalaryStructureUpdate(BaseModel):
    companyId: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None

class SalaryStructureResponse(SalaryStructureCreate):
    id: str
