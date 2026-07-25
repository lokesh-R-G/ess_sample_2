from pydantic import BaseModel
from typing import Optional

class PermissionOverflowRuleCreate(BaseModel):
    name: Optional[str] = None

class PermissionOverflowRuleUpdate(BaseModel):
    status: Optional[str] = None

class PermissionOverflowRuleResponse(PermissionOverflowRuleCreate):
    id: str
