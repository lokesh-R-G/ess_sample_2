from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class EmployeeGovernmentIdModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    employeeId: str
    panNumber: Optional[str] = None
    aadharNumber: Optional[str] = None
    uanNumber: Optional[str] = None
    pfNumber: Optional[str] = None
    esiNumber: Optional[str] = None
    passportNumber: Optional[str] = None
    status: str = "Active"
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    createdBy: Optional[str] = None
    updatedBy: Optional[str] = None
    deletedAt: Optional[datetime] = None
    deletedBy: Optional[str] = None
