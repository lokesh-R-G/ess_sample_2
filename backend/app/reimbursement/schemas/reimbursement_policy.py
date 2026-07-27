from pydantic import BaseModel
from typing import Optional

class ReimbursementPolicyCreate(BaseModel):
    pass

class ReimbursementPolicyUpdate(BaseModel):
    pass

class ReimbursementPolicyResponse(ReimbursementPolicyCreate):
    id: str
