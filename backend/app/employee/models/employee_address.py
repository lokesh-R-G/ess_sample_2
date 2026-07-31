from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class EmployeeAddressModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    employeeId: str
    currentAddressLine1: Optional[str] = None
    currentAddressLine2: Optional[str] = None
    currentCity: Optional[str] = None
    currentState: Optional[str] = None
    currentCountry: Optional[str] = None
    currentPincode: Optional[str] = None
    isSameAsCurrent: bool = False
    permanentAddressLine1: Optional[str] = None
    permanentAddressLine2: Optional[str] = None
    permanentCity: Optional[str] = None
    permanentState: Optional[str] = None
    permanentCountry: Optional[str] = None
    permanentPincode: Optional[str] = None
    status: str = "Active"
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    createdBy: Optional[str] = None
    updatedBy: Optional[str] = None
    deletedAt: Optional[datetime] = None
    deletedBy: Optional[str] = None
