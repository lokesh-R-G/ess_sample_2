from pydantic import BaseModel
from typing import Optional

class LeavePolicyCreate(BaseModel):
    pass

class LeavePolicyUpdate(BaseModel):
    pass

class LeavePolicyResponse(LeavePolicyCreate):
    id: str
