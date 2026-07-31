from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

class ESSLMachineSummary(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: str = Field(validation_alias="_id", serialization_alias="id")
    serialNumber: str
    ipAddress: Optional[str] = None
    status: Optional[str] = None

class BranchCreate(BaseModel):
    companyId: str
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
    companyId: Optional[str] = None
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

class BranchResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: str = Field(serialization_alias="_id")
    companyId: str
    name: str
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
    status: Optional[str] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    esslMachine: Optional[ESSLMachineSummary] = None
