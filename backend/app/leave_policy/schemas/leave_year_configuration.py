from pydantic import BaseModel
from typing import Optional

class LeaveYearConfigurationCreate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class LeaveYearConfigurationUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class LeaveYearConfigurationResponse(LeaveYearConfigurationCreate):
    id: str
