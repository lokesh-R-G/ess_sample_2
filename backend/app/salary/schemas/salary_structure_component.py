from pydantic import BaseModel
from typing import Optional

class SalaryStructureComponentCreate(BaseModel):
    name: Optional[str] = None

class SalaryStructureComponentUpdate(BaseModel):
    status: Optional[str] = None

class SalaryStructureComponentResponse(SalaryStructureComponentCreate):
    id: str
