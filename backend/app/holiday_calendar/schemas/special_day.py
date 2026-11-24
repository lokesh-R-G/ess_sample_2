from typing import Optional, List
from pydantic import BaseModel, Field, field_validator

class SpecialDayCreate(BaseModel):
    eventName: str = Field(..., min_length=1, max_length=200)
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    dayType: str = Field(..., description="'Sudden Holiday' or 'Sudden Cutoff'")
    applicability: str = Field(..., description="'All Branches' or 'Selected Branches'")
    selectedBranchIds: Optional[List[str]] = Field(default_factory=list)
    expectedWorkingHours: Optional[float] = Field(None, description="Required for Sudden Cutoff (0.5 to 24.0)")
    reason: Optional[str] = Field(None, max_length=1000)

    @field_validator("dayType")
    def validate_day_type(cls, v):
        if v not in ["Sudden Holiday", "Sudden Cutoff"]:
            raise ValueError("dayType must be either 'Sudden Holiday' or 'Sudden Cutoff'")
        return v

    @field_validator("applicability")
    def validate_applicability(cls, v):
        if v not in ["All Branches", "Selected Branches"]:
            raise ValueError("applicability must be either 'All Branches' or 'Selected Branches'")
        return v

    @field_validator("expectedWorkingHours")
    def validate_working_hours(cls, v, info):
        day_type = info.data.get("dayType")
        if day_type == "Sudden Cutoff":
            if v is None:
                raise ValueError("expectedWorkingHours is required for Sudden Cutoff")
            if v <= 0 or v > 24.0:
                raise ValueError("expectedWorkingHours must be greater than 0 and at most 24.0")
        elif day_type == "Sudden Holiday":
            if v is not None:
                # Sudden Holiday should not carry working hours
                return None
        return v

    @field_validator("selectedBranchIds")
    def validate_branch_ids(cls, v, info):
        applicability = info.data.get("applicability")
        if applicability == "Selected Branches" and not v:
            raise ValueError("selectedBranchIds must contain at least one branch for Selected Branches applicability")
        return v or []

class SpecialDayUpdate(BaseModel):
    eventName: Optional[str] = Field(None, min_length=1, max_length=200)
    reason: Optional[str] = Field(None, max_length=1000)
    expectedWorkingHours: Optional[float] = None
    status: Optional[str] = None  # "Active" | "Cancelled"

class SpecialDayResponse(BaseModel):
    id: str
    specialDayId: Optional[str] = None
    companyId: str
    eventName: str
    date: str
    dayType: str
    applicability: str
    selectedBranchIds: List[str] = []
    selectedBranchNames: Optional[List[str]] = []
    expectedWorkingHours: Optional[float] = None
    reason: Optional[str] = None
    status: str
    createdBy: Optional[str] = None
    createdAt: Optional[str] = None
    updatedBy: Optional[str] = None
    updatedAt: Optional[str] = None
    cancelledBy: Optional[str] = None
    cancelledAt: Optional[str] = None

class PaginatedSpecialDayResponse(BaseModel):
    total: int
    data: List[SpecialDayResponse]
