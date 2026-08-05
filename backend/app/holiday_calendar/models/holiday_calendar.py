from typing import Optional
from datetime import datetime, date
from pydantic import BaseModel, Field

class HolidayCalendarModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    calendarId: Optional[str] = None
    name: str
    description: Optional[str] = None
    year: int
    branchId: Optional[str] = None
    effectiveFrom: Optional[datetime] = None
    effectiveTo: Optional[datetime] = None
    
    # Hierarchy & Versioning
    status: str = "Active"
    
    # Audit
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    createdBy: Optional[str] = None
    updatedBy: Optional[str] = None
    deletedAt: Optional[datetime] = None
    deletedBy: Optional[str] = None

class HolidayDateModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    holidayId: Optional[str] = None
    calendarId: str
    holidayDate: date
    holidayName: str
    holidayType: str = "Mandatory" # Mandatory, Restricted, Optional, Branch, Festival, National
    isRecurring: bool = False
    remarks: Optional[str] = None
    
    status: str = "Active"
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    createdBy: Optional[str] = None
    updatedBy: Optional[str] = None
    deletedAt: Optional[datetime] = None
    deletedBy: Optional[str] = None
