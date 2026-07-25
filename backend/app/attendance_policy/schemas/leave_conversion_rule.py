from pydantic import BaseModel
from typing import Optional

class LeaveConversionRuleCreate(BaseModel):
    name: Optional[str] = None

class LeaveConversionRuleUpdate(BaseModel):
    status: Optional[str] = None

class LeaveConversionRuleResponse(LeaveConversionRuleCreate):
    id: str
