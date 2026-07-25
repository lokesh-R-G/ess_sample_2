from pydantic import BaseModel
from typing import Optional

class DeductionPolicyVersionCreate(BaseModel):
    status: Optional[str] = "Active"

class DeductionPolicyVersionUpdate(BaseModel):
    status: Optional[str] = None

class DeductionPolicyVersionResponse(DeductionPolicyVersionCreate):
    id: str
