from pydantic import BaseModel
from typing import Optional

class LeaveAttachmentCreate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class LeaveAttachmentUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class LeaveAttachmentResponse(LeaveAttachmentCreate):
    id: str
