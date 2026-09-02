from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class TripSheetModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    claimId: str
    tripDate: str  # YYYY-MM-DD
    fromLocation: str
    toLocation: str
    tripType: str  # "One Way", "Round Trip"
    
    startOdometer: float
    endOdometer: float
    claimedDistance: float
    calculatedDistance: float
    
    ratePerKm: float
    calculatedAmount: float
    
    # Audit
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    createdBy: Optional[str] = None
    updatedBy: Optional[str] = None
