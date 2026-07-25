from pydantic import BaseModel
from typing import Optional

class LeaveNegativeBalanceRuleCreate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class LeaveNegativeBalanceRuleUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class LeaveNegativeBalanceRuleResponse(LeaveNegativeBalanceRuleCreate):
    id: str
