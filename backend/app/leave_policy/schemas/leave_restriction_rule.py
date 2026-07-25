from pydantic import BaseModel
from typing import Optional

class LeaveRestrictionRuleCreate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class LeaveRestrictionRuleUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class LeaveRestrictionRuleResponse(LeaveRestrictionRuleCreate):
    id: str
