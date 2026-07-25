from pydantic import BaseModel
from typing import Optional

class PermissionAttachmentCreate(BaseModel):
    name: Optional[str] = None

class PermissionAttachmentUpdate(BaseModel):
    status: Optional[str] = None

class PermissionAttachmentResponse(PermissionAttachmentCreate):
    id: str
