from pydantic import BaseModel
from typing import Optional

class SalaryStructureVersionCreate(BaseModel):
    name: Optional[str] = None

class SalaryStructureVersionUpdate(BaseModel):
    status: Optional[str] = None

class SalaryStructureVersionResponse(SalaryStructureVersionCreate):
    id: str
