from pydantic import BaseModel
from typing import Optional

class MileageRatePolicyCreate(BaseModel):
    status: Optional[str] = "Active"

class MileageRatePolicyUpdate(BaseModel):
    status: Optional[str] = None

class MileageRatePolicyResponse(MileageRatePolicyCreate):
    id: str
