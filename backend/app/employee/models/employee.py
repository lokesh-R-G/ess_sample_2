from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class EmployeeModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    masterEmployeeId: Optional[str] = None
    employeeId: str
    employeeCode: Optional[str] = None
    machineId: Optional[str] = None
    systemAccessEnabled: bool = False
    authUserId: Optional[str] = None
    essStatus: str = "Not Invited"
    status: str = "Active"
    deactivatedAt: Optional[datetime] = None
    deactivatedBy: Optional[str] = None
    effectiveDeactivationDate: Optional[datetime] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    createdBy: Optional[str] = None
    updatedBy: Optional[str] = None
    deletedAt: Optional[datetime] = None
    deletedBy: Optional[str] = None
