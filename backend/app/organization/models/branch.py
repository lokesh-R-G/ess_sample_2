from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class BranchModel(BaseModel):
    model_config = ConfigDict(extra="allow")
    
    id: Optional[str] = Field(default=None, alias="_id")
    companyId: Optional[str] = None
    companyName: Optional[str] = None
    name: Optional[str] = None
    code: Optional[str] = None
    location: Optional[str] = None
    holidayCalendarId: Optional[str] = None
    weeklyOffPolicyId: Optional[str] = None
    
    status: str = "Active"
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    createdBy: Optional[str] = None
    updatedBy: Optional[str] = None
    deletedAt: Optional[datetime] = None
    deletedBy: Optional[str] = None

