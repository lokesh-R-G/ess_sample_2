from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class TripAllowancePolicyModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    companyId: str
    ratePerKm: float
    allowedTripTypes: list[str] = ["One Way", "Round Trip"]
    
    effectiveFrom: str  # YYYY-MM-DD
    effectiveTo: Optional[str] = None
    isActive: bool = True
    
    # Audit
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    createdBy: Optional[str] = None
    updatedBy: Optional[str] = None
