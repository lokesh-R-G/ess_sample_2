from pydantic import BaseModel
from typing import Optional

class PermissionHistoryCreate(BaseModel):
    name: Optional[str] = None

class PermissionHistoryUpdate(BaseModel):
    status: Optional[str] = None

class PermissionHistoryResponse(PermissionHistoryCreate):
    id: str
