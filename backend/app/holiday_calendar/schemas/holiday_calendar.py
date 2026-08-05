from typing import Optional, List
from pydantic import BaseModel, model_validator
from datetime import datetime, date

class HolidayCalendarCreate(BaseModel):
    name: str
    description: Optional[str] = None
    year: int
    branchId: Optional[str] = None
    effectiveFrom: Optional[datetime] = None
    effectiveTo: Optional[datetime] = None

    @model_validator(mode='after')
    def validate_effective_dates(self):
        if self.effectiveFrom and self.effectiveTo:
            if self.effectiveTo < self.effectiveFrom:
                raise ValueError("effectiveTo cannot be earlier than effectiveFrom")
        return self

class HolidayCalendarUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    year: Optional[int] = None
    branchId: Optional[str] = None
    effectiveFrom: Optional[datetime] = None
    effectiveTo: Optional[datetime] = None
    status: Optional[str] = None
    
    @model_validator(mode='after')
    def validate_effective_dates(self):
        if self.effectiveFrom and self.effectiveTo:
            if self.effectiveTo < self.effectiveFrom:
                raise ValueError("effectiveTo cannot be earlier than effectiveFrom")
        return self

class HolidayCalendarResponse(HolidayCalendarCreate):
    id: str
    calendarId: Optional[str] = None
    branchName: Optional[str] = None
    branchCode: Optional[str] = None
    holidayCount: Optional[int] = 0
    status: str
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

class PaginatedHolidayCalendarResponse(BaseModel):
    data: List[HolidayCalendarResponse]
    total: int
    page: int = 1
    pageSize: int = 100
    totalPages: int = 1

class HolidayDateCreate(BaseModel):
    holidayDate: date
    holidayName: str
    holidayType: str = "Mandatory"
    isRecurring: bool = False
    remarks: Optional[str] = None

class HolidayDateUpdate(BaseModel):
    holidayDate: Optional[date] = None
    holidayName: Optional[str] = None
    holidayType: Optional[str] = None
    isRecurring: Optional[bool] = None
    remarks: Optional[str] = None
    status: Optional[str] = None

class HolidayDateResponse(HolidayDateCreate):
    id: str
    calendarId: str
    holidayId: Optional[str] = None
    status: str
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
