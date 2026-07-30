from pydantic import BaseModel
from typing import Optional

class BranchCreate(BaseModel):
    name: str
    code: Optional[str] = None
    location: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    pincode: Optional[str] = None
    contactDetails: Optional[str] = None
    attendanceEnabled: bool = True
    esslMachineId: Optional[str] = None
    timezone: str = "Asia/Kolkata"

class BranchUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    location: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    pincode: Optional[str] = None
    contactDetails: Optional[str] = None
    attendanceEnabled: Optional[bool] = None
    esslMachineId: Optional[str] = None
    timezone: Optional[str] = None

class BranchResponse(BranchCreate):
    id: str
    companyId: str
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None
