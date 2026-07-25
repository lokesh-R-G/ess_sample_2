from pydantic import BaseModel
from typing import Optional

class SalaryRuleCreate(BaseModel):
    name: Optional[str] = None

class SalaryRuleUpdate(BaseModel):
    status: Optional[str] = None

class SalaryRuleResponse(SalaryRuleCreate):
    id: str
