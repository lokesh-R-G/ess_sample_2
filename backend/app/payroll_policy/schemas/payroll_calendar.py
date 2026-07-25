from pydantic import BaseModel
from typing import Optional

class PayrollCalendarCreate(BaseModel):
    status: Optional[str] = "Active"

class PayrollCalendarUpdate(BaseModel):
    status: Optional[str] = None

class PayrollCalendarResponse(PayrollCalendarCreate):
    id: str
