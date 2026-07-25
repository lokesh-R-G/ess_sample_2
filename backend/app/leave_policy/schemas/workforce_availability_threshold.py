from pydantic import BaseModel
from typing import Optional

class WorkforceAvailabilityThresholdCreate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class WorkforceAvailabilityThresholdUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class WorkforceAvailabilityThresholdResponse(WorkforceAvailabilityThresholdCreate):
    id: str
