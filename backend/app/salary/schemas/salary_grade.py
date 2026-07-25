from pydantic import BaseModel
from typing import Optional

class SalaryGradeCreate(BaseModel):
    name: Optional[str] = None

class SalaryGradeUpdate(BaseModel):
    status: Optional[str] = None

class SalaryGradeResponse(SalaryGradeCreate):
    id: str
