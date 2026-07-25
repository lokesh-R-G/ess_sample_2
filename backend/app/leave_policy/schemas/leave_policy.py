from pydantic import BaseModel
from typing import Optional

class LeavePolicyCreate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class LeavePolicyUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class LeavePolicyResponse(LeavePolicyCreate):
    id: str
