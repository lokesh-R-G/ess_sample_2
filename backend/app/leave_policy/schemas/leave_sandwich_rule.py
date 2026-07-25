from pydantic import BaseModel
from typing import Optional

class LeaveSandwichRuleCreate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class LeaveSandwichRuleUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class LeaveSandwichRuleResponse(LeaveSandwichRuleCreate):
    id: str
