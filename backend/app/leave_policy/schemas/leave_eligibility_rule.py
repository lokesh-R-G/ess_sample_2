from pydantic import BaseModel
from typing import Optional

class LeaveEligibilityRuleCreate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class LeaveEligibilityRuleUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class LeaveEligibilityRuleResponse(LeaveEligibilityRuleCreate):
    id: str
