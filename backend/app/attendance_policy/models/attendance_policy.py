from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class AttendancePolicyModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    attendancePolicyCode: Optional[str] = None
    name: str
    description: Optional[str] = None
    
    # Grace Rules
    graceInMinutes: int = 0
    graceOutMinutes: int = 0
    
    # Hour Thresholds
    minHoursForFullDay: float = 8.0
    minHoursForHalfDay: float = 4.0
    absentHoursThreshold: float = 2.0
    lopHalfDayHours: float = 4.0
    lopFullDayHours: float = 8.0
    
    # Penalties
    lateInThresholdMinutes: int = 15
    earlyOutThresholdMinutes: int = 15
    lateIncrementThreshold: int = 3
    lateHalfDayThreshold: int = 3
    lateFullDayThreshold: int = 6
    
    # Hierarchy & Versioning
    version: int = 1
    status: str = "Active"
    isCurrent: bool = True
    effectiveFrom: Optional[datetime] = None
    effectiveTo: Optional[datetime] = None
    
    # Audit
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    createdBy: Optional[str] = None
    updatedBy: Optional[str] = None
    deletedAt: Optional[datetime] = None
    deletedBy: Optional[str] = None
