from pydantic import BaseModel
from typing import Optional

class LatePolicyCreate(BaseModel):
    name: Optional[str] = None

class LatePolicyUpdate(BaseModel):
    status: Optional[str] = None

class LatePolicyResponse(LatePolicyCreate):
    id: str
