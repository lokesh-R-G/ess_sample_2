from pydantic import BaseModel
from typing import Optional

class PermissionRequestCreate(BaseModel):
    name: Optional[str] = None

class PermissionRequestUpdate(BaseModel):
    status: Optional[str] = None

class PermissionRequestResponse(PermissionRequestCreate):
    id: str
