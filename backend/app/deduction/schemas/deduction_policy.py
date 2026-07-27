from pydantic import BaseModel
from typing import Optional

class DeductionPolicyCreate(BaseModel):
    pass

class DeductionPolicyUpdate(BaseModel):
    pass

class DeductionPolicyResponse(DeductionPolicyCreate):
    id: str
