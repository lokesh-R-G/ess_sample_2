from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

from app.attendance_policy.models.weekly_off_policy import DaySchedule

class WeeklyOffPolicyCreate(BaseModel):
    name: str
    description: Optional[str] = None
    monday: Optional[DaySchedule] = None
    tuesday: Optional[DaySchedule] = None
    wednesday: Optional[DaySchedule] = None
    thursday: Optional[DaySchedule] = None
    friday: Optional[DaySchedule] = None
    saturday: Optional[DaySchedule] = None
    sunday: Optional[DaySchedule] = None
    effectiveFrom: Optional[datetime] = None
    effectiveTo: Optional[datetime] = None

class WeeklyOffPolicyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    monday: Optional[DaySchedule] = None
    tuesday: Optional[DaySchedule] = None
    wednesday: Optional[DaySchedule] = None
    thursday: Optional[DaySchedule] = None
    friday: Optional[DaySchedule] = None
    saturday: Optional[DaySchedule] = None
    sunday: Optional[DaySchedule] = None
    status: Optional[str] = None
    isCurrent: Optional[bool] = None
    effectiveFrom: Optional[datetime] = None
    effectiveTo: Optional[datetime] = None

class WeeklyOffPolicyResponse(WeeklyOffPolicyCreate):
    id: str
    status: str
    isCurrent: bool
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

class PaginatedWeeklyOffPolicyResponse(BaseModel):
    data: List[WeeklyOffPolicyResponse]
    total: int
    page: int = 1
    pageSize: int = 100
    totalPages: int = 1
