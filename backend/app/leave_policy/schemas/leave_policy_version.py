from pydantic import BaseModel
from typing import Optional

class LeavePolicyVersionCreate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class LeavePolicyVersionUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class LeavePolicyVersionResponse(LeavePolicyVersionCreate):
    id: str
