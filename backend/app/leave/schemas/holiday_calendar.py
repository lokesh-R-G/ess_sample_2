from pydantic import BaseModel
from typing import Optional

class HolidayCalendarCreate(BaseModel):
    pass

class HolidayCalendarUpdate(BaseModel):
    pass

class HolidayCalendarResponse(HolidayCalendarCreate):
    id: str
