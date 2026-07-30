from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime

class ESSLMachineCreate(BaseModel):
    serialNumber: str
    ipAddress: Optional[str] = None
    status: Literal["Active", "Offline", "Maintenance"] = "Active"
    
class ESSLMachineUpdate(BaseModel):
    serialNumber: Optional[str] = None
    ipAddress: Optional[str] = None
    status: Optional[Literal["Active", "Offline", "Maintenance"]] = None
    lastSyncAt: Optional[datetime] = None

class ESSLMachineResponse(ESSLMachineCreate):
    id: str
    lastSyncAt: Optional[datetime] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None
