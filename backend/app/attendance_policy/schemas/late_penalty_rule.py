from pydantic import BaseModel
from typing import Optional

class LatePenaltyRuleCreate(BaseModel):
    name: Optional[str] = None

class LatePenaltyRuleUpdate(BaseModel):
    status: Optional[str] = None

class LatePenaltyRuleResponse(LatePenaltyRuleCreate):
    id: str
