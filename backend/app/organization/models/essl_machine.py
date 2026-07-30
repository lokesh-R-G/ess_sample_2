from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class ESSLMachineModel(BaseModel):
    model_config = ConfigDict(extra="allow")
    
    id: Optional[str] = Field(default=None, alias="_id")
    name: str
    serialNumber: str
    vendor: Optional[str] = None
    model: Optional[str] = None
    firmwareVersion: Optional[str] = None
    ipAddress: Optional[str] = None
    port: Optional[int] = None
    communicationType: Optional[str] = None
    location: Optional[str] = None
    remarks: Optional[str] = None
    status: str = "Active"
    
    # Audit fields
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    createdBy: Optional[str] = None
    updatedBy: Optional[str] = None
    deletedAt: Optional[datetime] = None
    deletedBy: Optional[str] = None
