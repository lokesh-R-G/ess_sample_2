from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

# Assuming BaseDBModel might not exist in organization module, we'll just inherit BaseModel if needed.
# Let's import BaseDBModel from app.db.base_model if available, else just use BaseModel.
# Wait, other models in organization use BaseModel. Let's just use BaseModel for now.

class ShiftModel(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)
    
    id: Optional[str] = Field(default=None, alias="_id")
    shiftCode: str
    name: str
    description: Optional[str] = None
    
    # Relationships
    attendancePolicyCode: Optional[str] = None
    attendancePolicyId: Optional[str] = None
    weeklyOffPolicyCode: Optional[str] = None
    weeklyOffPolicyId: Optional[str] = None
    
    # Standard Timings
    startTime: str
    endTime: str
    
    # Break Rules
    breakStartTime: Optional[str] = None
    breakEndTime: Optional[str] = None
    autoPunchLunchOut: bool = False
    autoPunchLunchIn: bool = False
    
    # Advanced 
    isCrossMidnight: bool = False
    
    # Versioning
    version: int = 1
    isCurrent: bool = True
    effectiveFrom: Optional[datetime] = None
    effectiveTo: Optional[datetime] = None
    
    # Standard DB / Audit Fields
    status: str = "Active"
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    createdBy: Optional[str] = None
    updatedBy: Optional[str] = None
    deletedAt: Optional[datetime] = None
    deletedBy: Optional[str] = None
