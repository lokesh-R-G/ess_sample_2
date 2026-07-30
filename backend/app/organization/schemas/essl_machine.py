from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

class ESSLMachineCreate(BaseModel):
    serialNumber: str
    vendor: Optional[str] = None
    model: Optional[str] = None
    firmwareVersion: Optional[str] = None
    ipAddress: Optional[str] = None
    port: Optional[int] = None
    communicationType: Optional[str] = None
    location: Optional[str] = None
    remarks: Optional[str] = None
    status: Literal["Active", "Offline", "Maintenance"] = "Active"
    
class ESSLMachineUpdate(BaseModel):
    serialNumber: Optional[str] = None
    vendor: Optional[str] = None
    model: Optional[str] = None
    firmwareVersion: Optional[str] = None
    ipAddress: Optional[str] = None
    port: Optional[int] = None
    communicationType: Optional[str] = None
    location: Optional[str] = None
    remarks: Optional[str] = None
    status: Optional[Literal["Active", "Offline", "Maintenance"]] = None

class ESSLMachineResponse(ESSLMachineCreate):
    id: str = Field(alias="_id")
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    createdBy: Optional[str] = None
    updatedBy: Optional[str] = None
