from pydantic import BaseModel
from typing import Optional

class GracePolicyCreate(BaseModel):
    name: Optional[str] = None

class GracePolicyUpdate(BaseModel):
    status: Optional[str] = None

class GracePolicyResponse(GracePolicyCreate):
    id: str
