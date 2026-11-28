from typing import Optional, List
from pydantic import BaseModel, Field, field_validator

class SpecialDayCreate(BaseModel):
    eventName: str = Field(..., min_length=1, max_length=200)
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    dayType: str = Field(..., description="'Sudden Holiday', 'Sudden Shift Change', or 'Sudden Cutoff'")
    
    # Scope hierarchy: "GLOBAL" | "SELECTED_COMPANIES" | "SINGLE_COMPANY"
    scopeType: str = Field(default="SINGLE_COMPANY", description="'GLOBAL', 'SELECTED_COMPANIES', or 'SINGLE_COMPANY'")
    companyId: Optional[str] = Field(None, description="Company ID for SINGLE_COMPANY")
    companyIds: Optional[List[str]] = Field(default_factory=list, description="Company IDs for SELECTED_COMPANIES")
    
    applicability: str = Field(..., description="'All Branches' or 'Selected Branches'")
    selectedBranchIds: Optional[List[str]] = Field(default_factory=list)

    # Shift timing fields for Sudden Shift Change
    shiftId: Optional[str] = None
    shiftCode: Optional[str] = None
    startTime: Optional[str] = Field(None, description="Expected IN time (HH:MM or HH:MM:SS)")
    endTime: Optional[str] = Field(None, description="Expected OUT time (HH:MM or HH:MM:SS)")
    expectedWorkingHours: Optional[float] = Field(None, description="Expected working hours")
    isCrossMidnight: bool = False
    breakStartTime: Optional[str] = None
    breakEndTime: Optional[str] = None

    reason: Optional[str] = Field(None, max_length=1000)

    @field_validator("dayType")
    def validate_day_type(cls, v):
        valid = ["Sudden Holiday", "Sudden Shift Change", "Sudden Cutoff"]
        if v not in valid:
            raise ValueError(f"dayType must be one of {valid}")
        return v

    @field_validator("scopeType")
    def validate_scope_type(cls, v):
        valid = ["GLOBAL", "SELECTED_COMPANIES", "SINGLE_COMPANY"]
        if v not in valid:
            raise ValueError(f"scopeType must be one of {valid}")
        return v

    @field_validator("applicability")
    def validate_applicability(cls, v):
        if v not in ["All Branches", "Selected Branches"]:
            raise ValueError("applicability must be either 'All Branches' or 'Selected Branches'")
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
    startTime: Optional[str] = None
    endTime: Optional[str] = None
    expectedWorkingHours: Optional[float] = None
    isCrossMidnight: Optional[bool] = None
    breakStartTime: Optional[str] = None
    breakEndTime: Optional[str] = None
    status: Optional[str] = None  # "Active" | "Cancelled"

class SpecialDayResponse(BaseModel):
    id: str
    specialDayId: Optional[str] = None
    scopeType: str = "SINGLE_COMPANY"
    companyId: Optional[str] = None
    companyIds: List[str] = []
    companyNames: Optional[List[str]] = []
    eventName: str
    date: str
    dayType: str
    applicability: str
    selectedBranchIds: List[str] = []
    selectedBranchNames: Optional[List[str]] = []
    shiftId: Optional[str] = None
    shiftCode: Optional[str] = None
    startTime: Optional[str] = None
    endTime: Optional[str] = None
    expectedWorkingHours: Optional[float] = None
    isCrossMidnight: bool = False
    breakStartTime: Optional[str] = None
    breakEndTime: Optional[str] = None
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
