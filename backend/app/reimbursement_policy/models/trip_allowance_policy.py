from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class TripAllowancePolicyModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    companyId: str
    ratePerKm: float
    allowedTripTypes: list[str] = ["One Way", "Round Trip"]
    policyCode: str = "TRIP_ALL_DEFAULT"
    version: int = 1
    isCurrent: bool = True
    
    effectiveFrom: str  # YYYY-MM-DD
    effectiveTo: Optional[str] = None
    
    # Audit
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    createdBy: Optional[str] = None
    updatedBy: Optional[str] = None
