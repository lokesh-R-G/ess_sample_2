from typing import Optional, List, Dict
from datetime import datetime
from pydantic import BaseModel, Field

class WeeklyOffDayRule(BaseModel):
    dayOfWeek: int # 0=Monday, 6=Sunday
    weekNumbers: List[int] # [1, 2, 3, 4, 5] means every week, [1, 3] means 1st and 3rd week

class WeeklyOffPolicyModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    name: str
    description: Optional[str] = None
    
    rules: List[WeeklyOffDayRule] = []
    
    # Hierarchy & Versioning
    status: str = "Active"
    isCurrent: bool = True
    effectiveFrom: Optional[datetime] = None
    effectiveTo: Optional[datetime] = None
    
    # Audit
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    createdBy: Optional[str] = None
    updatedBy: Optional[str] = None
    deletedAt: Optional[datetime] = None
    deletedBy: Optional[str] = None
