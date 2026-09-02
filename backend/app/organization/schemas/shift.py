from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

class ShiftCreate(BaseModel):
    shiftCode: str
    name: str
    description: Optional[str] = None
    attendancePolicyId: str
    attendancePolicyCode: Optional[str] = None
    weeklyOffPolicyId: Optional[str] = None
    weeklyOffPolicyCode: Optional[str] = None
    
    startTime: str          # HH:MM format
    endTime: str            # HH:MM format
    
    breakStartTime: Optional[str] = None
    breakEndTime: Optional[str] = None
    autoPunchLunchOut: bool = False
    autoPunchLunchIn: bool = False
    
    isCrossMidnight: bool = False
    
    effectiveFrom: Optional[datetime] = None
    effectiveTo: Optional[datetime] = None

class ShiftUpdate(BaseModel):
    shiftCode: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    attendancePolicyId: Optional[str] = None
    attendancePolicyCode: Optional[str] = None
    weeklyOffPolicyId: Optional[str] = None
    weeklyOffPolicyCode: Optional[str] = None
    
    startTime: Optional[str] = None
    endTime: Optional[str] = None
    
    breakStartTime: Optional[str] = None
    breakEndTime: Optional[str] = None
    autoPunchLunchOut: Optional[bool] = None
    autoPunchLunchIn: Optional[bool] = None
    
    isCrossMidnight: Optional[bool] = None
    
    status: Optional[str] = None
    isCurrent: Optional[bool] = None
    effectiveFrom: Optional[datetime] = None
    effectiveTo: Optional[datetime] = None

class ShiftResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: str = Field(serialization_alias="_id")
    shiftCode: str
    name: str
    description: Optional[str] = None
    attendancePolicyId: str
    attendancePolicyCode: Optional[str] = None
    weeklyOffPolicyId: Optional[str] = None
    weeklyOffPolicyCode: Optional[str] = None
    
    startTime: str
    endTime: str
    
    breakStartTime: Optional[str] = None
    breakEndTime: Optional[str] = None
    autoPunchLunchOut: bool = False
    autoPunchLunchIn: bool = False
    
    isCrossMidnight: bool = False
    
    version: int = 1
    isCurrent: bool = True
    effectiveFrom: Optional[datetime] = None
    effectiveTo: Optional[datetime] = None
    
    status: Optional[str] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
