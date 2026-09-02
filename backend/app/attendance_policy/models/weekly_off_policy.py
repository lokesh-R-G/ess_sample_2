from typing import Optional, List, Dict
from datetime import datetime
from pydantic import BaseModel, Field

from enum import Enum

class DayType(str, Enum):
    WORKING = "WORKING"
    WEEKOFF = "WEEKOFF"
    CUTOFF = "CUTOFF"

class DaySchedule(BaseModel):
    enabled: bool = True
    dayType: DayType = DayType.WORKING
    startTime: Optional[str] = None
    endTime: Optional[str] = None
    remarks: Optional[str] = None

class WeeklyOffPolicyModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    weeklyOffPolicyCode: Optional[str] = None
    name: str
    description: Optional[str] = None
    
    monday: DaySchedule = Field(default_factory=DaySchedule)
    tuesday: DaySchedule = Field(default_factory=DaySchedule)
    wednesday: DaySchedule = Field(default_factory=DaySchedule)
    thursday: DaySchedule = Field(default_factory=DaySchedule)
    friday: DaySchedule = Field(default_factory=DaySchedule)
    saturday: DaySchedule = Field(default_factory=DaySchedule)
    sunday: DaySchedule = Field(default_factory=lambda: DaySchedule(dayType=DayType.WEEKOFF))
    
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
