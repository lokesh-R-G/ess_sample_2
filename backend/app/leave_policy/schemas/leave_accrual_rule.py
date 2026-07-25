from pydantic import BaseModel
from typing import Optional

class LeaveAccrualRuleCreate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class LeaveAccrualRuleUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class LeaveAccrualRuleResponse(LeaveAccrualRuleCreate):
    id: str
