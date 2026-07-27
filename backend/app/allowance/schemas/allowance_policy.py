from pydantic import BaseModel
from typing import Optional

class AllowancePolicyCreate(BaseModel):
    pass

class AllowancePolicyUpdate(BaseModel):
    pass

class AllowancePolicyResponse(AllowancePolicyCreate):
    id: str
