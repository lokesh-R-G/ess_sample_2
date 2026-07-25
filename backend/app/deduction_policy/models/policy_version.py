from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class PolicyVersionModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    version: int
    effectiveFrom: datetime
    effectiveUntil: Optional[datetime]
    status: str = "Active"
    createdBy: str
    approvedBy: Optional[str]
    approvalDate: Optional[datetime]
    reason: str
    configData: dict
