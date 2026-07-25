from pydantic import BaseModel
from typing import Optional

class LeaveCarryForwardRuleCreate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class LeaveCarryForwardRuleUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class LeaveCarryForwardRuleResponse(LeaveCarryForwardRuleCreate):
    id: str
