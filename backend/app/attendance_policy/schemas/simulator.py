from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SimulationRequest(BaseModel):
    employeeId: str
    shiftId: str
    scheduledIn: datetime
    scheduledOut: datetime
    actualIn: datetime
    actualOut: datetime
    permissionRequestedMinutes: int = 0
    currentLateCount: int = 0
    currentPermissionBalanceMinutes: int = 0
    policyVersionId: Optional[str] = None

class SimulationResponse(BaseModel):
    graceUsedMinutes: int
    graceApproved: bool
    lateMinutes: int
    lateCountAfterCalculation: int
    permissionUsedMinutes: int
    permissionRemainingMinutes: int
    permissionOverflowMinutes: int
    leaveDeduction: float
    penaltyApplied: str
    attendanceStatus: str
    calculationTrace: list[str]
