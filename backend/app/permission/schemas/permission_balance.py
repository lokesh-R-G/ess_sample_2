from pydantic import BaseModel
from typing import Optional

class PermissionBalanceCreate(BaseModel):
    name: Optional[str] = None

class PermissionBalanceUpdate(BaseModel):
    status: Optional[str] = None

class PermissionBalanceResponse(PermissionBalanceCreate):
    id: str
