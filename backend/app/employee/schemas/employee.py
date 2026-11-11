from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class EmployeeCreate(BaseModel):
    employeeCode: Optional[str] = None
    machineId: Optional[str] = None

class EmployeeUpdate(BaseModel):
    status: Optional[str] = None
    systemAccessEnabled: Optional[bool] = None
    authUserId: Optional[str] = None
    essStatus: Optional[str] = None
    employeeCode: Optional[str] = None
    machineId: Optional[str] = None

class EmployeeResponse(BaseModel):
    id: str
    employeeId: str
    employeeCode: Optional[str] = None
    machineId: Optional[str] = None
    systemAccessEnabled: bool
    authUserId: Optional[str] = None
    essStatus: str
    status: str
    deactivatedAt: Optional[datetime] = None
    effectiveDeactivationDate: Optional[datetime] = None
