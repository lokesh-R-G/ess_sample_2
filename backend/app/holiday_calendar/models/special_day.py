from typing import Optional, List
from datetime import datetime, date
from pydantic import BaseModel, Field, ConfigDict

class SpecialDayModel(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: Optional[str] = Field(default=None, alias="_id")
    specialDayId: Optional[str] = None
    companyId: str
    eventName: str
    date: str  # YYYY-MM-DD
    dayType: str  # "Sudden Holiday" | "Sudden Shift Change" | "Sudden Cutoff"
    applicability: str  # "All Branches" | "Selected Branches"
    selectedBranchIds: List[str] = Field(default_factory=list)

    # Shift timing parameters for Sudden Shift Change
    shiftId: Optional[str] = None
    shiftCode: Optional[str] = None
    startTime: Optional[str] = None
    endTime: Optional[str] = None
    expectedWorkingHours: Optional[float] = None
    isCrossMidnight: bool = False
    breakStartTime: Optional[str] = None
    breakEndTime: Optional[str] = None

    reason: Optional[str] = None
    status: str = "Active"  # "Active" | "Cancelled"

    # Audit fields
    createdBy: Optional[str] = None
    createdAt: Optional[datetime] = None
    updatedBy: Optional[str] = None
    updatedAt: Optional[datetime] = None
    cancelledBy: Optional[str] = None
    cancelledAt: Optional[datetime] = None
