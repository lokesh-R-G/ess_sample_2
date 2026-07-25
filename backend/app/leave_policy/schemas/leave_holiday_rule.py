from pydantic import BaseModel
from typing import Optional

class LeaveHolidayRuleCreate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class LeaveHolidayRuleUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class LeaveHolidayRuleResponse(LeaveHolidayRuleCreate):
    id: str
