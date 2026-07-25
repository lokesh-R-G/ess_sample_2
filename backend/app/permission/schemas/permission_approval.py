from pydantic import BaseModel
from typing import Optional

class PermissionApprovalCreate(BaseModel):
    name: Optional[str] = None

class PermissionApprovalUpdate(BaseModel):
    status: Optional[str] = None

class PermissionApprovalResponse(PermissionApprovalCreate):
    id: str
