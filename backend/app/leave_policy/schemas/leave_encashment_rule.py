from pydantic import BaseModel
from typing import Optional

class LeaveEncashmentRuleCreate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class LeaveEncashmentRuleUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class LeaveEncashmentRuleResponse(LeaveEncashmentRuleCreate):
    id: str
