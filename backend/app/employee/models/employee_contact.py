from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class EmployeeContactModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    employeeId: str
    workEmail: Optional[str] = None
    mobilePhone: Optional[str] = None
    personalEmail: Optional[str] = None
    personalMobile: Optional[str] = None
    emergencyContactName: Optional[str] = None
    emergencyContactNumber: Optional[str] = None
    emergencyContactRelation: Optional[str] = None
    status: str = "Active"
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    createdBy: Optional[str] = None
    updatedBy: Optional[str] = None
    deletedAt: Optional[datetime] = None
    deletedBy: Optional[str] = None
