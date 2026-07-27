from pydantic import BaseModel
from typing import Optional

class ReimbursementClaimCreate(BaseModel):
    pass

class ReimbursementClaimUpdate(BaseModel):
    pass

class ReimbursementClaimResponse(ReimbursementClaimCreate):
    id: str
