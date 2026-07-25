from pydantic import BaseModel
from typing import Optional

class PermissionUsageCreate(BaseModel):
    name: Optional[str] = None

class PermissionUsageUpdate(BaseModel):
    status: Optional[str] = None

class PermissionUsageResponse(PermissionUsageCreate):
    id: str
