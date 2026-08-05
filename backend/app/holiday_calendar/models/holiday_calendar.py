from typing import Optional
from datetime import datetime, date
from pydantic import BaseModel, Field

class HolidayCalendarModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    name: str
    description: Optional[str] = None
    year: int
    
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
    calendarId: str
    date: date
    name: str
    type: str = "Mandatory" # Mandatory, Restricted, Optional
    
    status: str = "Active"
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    createdBy: Optional[str] = None
    updatedBy: Optional[str] = None
    deletedAt: Optional[datetime] = None
    deletedBy: Optional[str] = None
