from pydantic import BaseModel
from typing import Optional

class LeavePenaltyRuleCreate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class LeavePenaltyRuleUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class LeavePenaltyRuleResponse(LeavePenaltyRuleCreate):
    id: str
