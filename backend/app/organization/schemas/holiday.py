from pydantic import BaseModel
from typing import Optional

class HolidayCreate(BaseModel):
    name: str

class HolidayUpdate(BaseModel):
    name: Optional[str] = None

class HolidayResponse(HolidayCreate):
    id: str
