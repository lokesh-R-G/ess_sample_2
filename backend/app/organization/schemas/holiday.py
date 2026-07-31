from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, date
from typing import Optional

class HolidayCreate(BaseModel):
    companyId: str
    name: str
    date: str               # ISO date string e.g. "2026-08-15"
    description: Optional[str] = None

class HolidayUpdate(BaseModel):
    companyId: Optional[str] = None
    name: Optional[str] = None
    date: Optional[str] = None
    description: Optional[str] = None

class HolidayResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: str = Field(serialization_alias="_id")
    companyId: str
    name: str
    date: str
    description: Optional[str] = None
    status: Optional[str] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
