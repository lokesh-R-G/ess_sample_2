from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ScheduledJobModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    jobName: str
    cronExpression: str
    nextRun: datetime
    lastRun: Optional[datetime] = None
    status: str = "Active"
    retryCount: int = 0
