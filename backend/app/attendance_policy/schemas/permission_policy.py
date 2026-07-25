from pydantic import BaseModel
from typing import Optional

class PermissionPolicyCreate(BaseModel):
    name: Optional[str] = None

class PermissionPolicyUpdate(BaseModel):
    status: Optional[str] = None

class PermissionPolicyResponse(PermissionPolicyCreate):
    id: str
