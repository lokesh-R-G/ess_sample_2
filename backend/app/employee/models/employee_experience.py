from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class EmployeeExperienceModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    employeeId: str
    status: str = "Active"
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    createdBy: Optional[str] = None
    updatedBy: Optional[str] = None
    deletedAt: Optional[datetime] = None
    deletedBy: Optional[str] = None
