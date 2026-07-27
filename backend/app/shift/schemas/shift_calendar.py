from pydantic import BaseModel
from typing import Optional

class ShiftCalendarCreate(BaseModel):
    pass

class ShiftCalendarUpdate(BaseModel):
    pass

class ShiftCalendarResponse(ShiftCalendarCreate):
    id: str
