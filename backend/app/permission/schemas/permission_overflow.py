from pydantic import BaseModel
from typing import Optional

class PermissionOverflowCreate(BaseModel):
    name: Optional[str] = None

class PermissionOverflowUpdate(BaseModel):
    status: Optional[str] = None

class PermissionOverflowResponse(PermissionOverflowCreate):
    id: str
