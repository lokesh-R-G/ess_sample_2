from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

class AttendancePolicyCreate(BaseModel):
    attendancePolicyCode: str
    name: str
    description: Optional[str] = None
    graceInMinutes: int = 0
    graceOutMinutes: int = 0
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

    # Permission Rules
    permissionMinutes: int = 60
    permissionPerMonth: int = 2
    monthlyPermissionHours: float = 1.0
    permissionExcessCarryForward: bool = True
    permissionLopThresholdMinutes: int = 240
    permissionLopValue: float = 0.5
    effectiveFrom: Optional[datetime] = None
    effectiveTo: Optional[datetime] = None

class AttendancePolicyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    graceInMinutes: Optional[int] = None
    graceOutMinutes: Optional[int] = None
    minHoursForFullDay: Optional[float] = None
    minHoursForHalfDay: Optional[float] = None
    absentHoursThreshold: Optional[float] = None
    lopHalfDayHours: Optional[float] = None
    lopFullDayHours: Optional[float] = None
    
    # Penalties
    lateInThresholdMinutes: Optional[int] = None
    earlyOutThresholdMinutes: Optional[int] = None
    lateIncrementThreshold: Optional[int] = None
    lateHalfDayThreshold: Optional[int] = None
    lateFullDayThreshold: Optional[int] = None
    
    # Permission Rules
    permissionMinutes: Optional[int] = None
    permissionPerMonth: Optional[int] = None
    monthlyPermissionHours: Optional[float] = None
    permissionExcessCarryForward: Optional[bool] = None
    permissionLopThresholdMinutes: Optional[int] = None
    permissionLopValue: Optional[float] = None
    status: Optional[str] = None
    isCurrent: Optional[bool] = None
    effectiveFrom: Optional[datetime] = None
    effectiveTo: Optional[datetime] = None

class AttendancePolicyResponse(AttendancePolicyCreate):
    id: str
    version: int
    status: str
    isCurrent: bool
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

class PaginatedAttendancePolicyResponse(BaseModel):
    data: List[AttendancePolicyResponse]
    total: int
    page: int = 1
    pageSize: int = 100
    totalPages: int = 1
