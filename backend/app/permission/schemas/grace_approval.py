from pydantic import BaseModel
from typing import Optional

class GraceApprovalCreate(BaseModel):
    name: Optional[str] = None

class GraceApprovalUpdate(BaseModel):
    status: Optional[str] = None

class GraceApprovalResponse(GraceApprovalCreate):
    id: str
