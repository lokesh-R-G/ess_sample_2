from pydantic import BaseModel
from typing import Optional

class EmployeeAddressCreate(BaseModel):
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

class EmployeeAddressUpdate(BaseModel):
    status: Optional[str] = None
    currentAddressLine1: Optional[str] = None
    currentAddressLine2: Optional[str] = None
    currentCity: Optional[str] = None
    currentState: Optional[str] = None
    currentCountry: Optional[str] = None
    currentPincode: Optional[str] = None
    isSameAsCurrent: Optional[bool] = None
    permanentAddressLine1: Optional[str] = None
    permanentAddressLine2: Optional[str] = None
    permanentCity: Optional[str] = None
    permanentState: Optional[str] = None
    permanentCountry: Optional[str] = None
    permanentPincode: Optional[str] = None

class EmployeeAddressResponse(EmployeeAddressCreate):
    id: str
    status: str
