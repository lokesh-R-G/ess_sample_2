from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

class WeeklyOffDayRuleSchema(BaseModel):
    dayOfWeek: int
    weekNumbers: List[int]

class WeeklyOffPolicyCreate(BaseModel):
    name: str
    description: Optional[str] = None
    rules: List[WeeklyOffDayRuleSchema] = []
    effectiveFrom: Optional[datetime] = None
    effectiveTo: Optional[datetime] = None

class WeeklyOffPolicyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    rules: Optional[List[WeeklyOffDayRuleSchema]] = None
    status: Optional[str] = None
    isCurrent: Optional[bool] = None
    effectiveFrom: Optional[datetime] = None
    effectiveTo: Optional[datetime] = None

class WeeklyOffPolicyResponse(WeeklyOffPolicyCreate):
    id: str
    status: str
    isCurrent: bool
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
