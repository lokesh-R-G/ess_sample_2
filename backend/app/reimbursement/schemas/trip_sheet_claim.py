from pydantic import BaseModel
from typing import Optional

class TripSheetClaimCreate(BaseModel):
    status: Optional[str] = "Active"

class TripSheetClaimUpdate(BaseModel):
    status: Optional[str] = None

class TripSheetClaimResponse(TripSheetClaimCreate):
    id: str
