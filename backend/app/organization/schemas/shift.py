from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

class ShiftCreate(BaseModel):
    companyId: str
    name: str
    startTime: str          # HH:MM format
    endTime: str            # HH:MM format
    gracePeriodMinutes: int = 0

class ShiftUpdate(BaseModel):
    companyId: Optional[str] = None
    name: Optional[str] = None
    startTime: Optional[str] = None
    endTime: Optional[str] = None
    gracePeriodMinutes: Optional[int] = None

class ShiftResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: str = Field(serialization_alias="_id")
    companyId: str
    name: str
    startTime: str
    endTime: str
    gracePeriodMinutes: int = 0
    status: Optional[str] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
