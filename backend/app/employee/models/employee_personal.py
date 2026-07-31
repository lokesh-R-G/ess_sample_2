from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class EmployeePersonalModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    employeeId: str
    firstName: str = ""
    lastName: str = ""
    middleName: Optional[str] = None
    dob: Optional[datetime] = None
    gender: Optional[str] = None
    maritalStatus: Optional[str] = None
    bloodGroup: Optional[str] = None
    nationality: Optional[str] = None
    status: str = "Active"
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    createdBy: Optional[str] = None
    updatedBy: Optional[str] = None
    deletedAt: Optional[datetime] = None
    deletedBy: Optional[str] = None
