from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime, date

class HolidayCalendarCreate(BaseModel):
    name: str
    description: Optional[str] = None
    year: int

class HolidayCalendarUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    year: Optional[int] = None
    status: Optional[str] = None

class HolidayCalendarResponse(HolidayCalendarCreate):
    id: str
    status: str
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

class HolidayDateCreate(BaseModel):
    calendarId: str
    date: date
    name: str
    type: str = "Mandatory"

class HolidayDateUpdate(BaseModel):
    date: Optional[date] = None
    name: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None

class HolidayDateResponse(HolidayDateCreate):
    id: str
    status: str
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
