from typing import Optional
from datetime import datetime, date
from pydantic import BaseModel, Field

class AttendanceDirtyQueueModel(BaseModel):
    dirtyId: str = Field(..., description="Unique identifier for this dirty queue record")
    employeeId: str
    employeeCode: str
    fromDate: str # ISO format date string e.g., "2026-08-01"
    toDate: str
    reason: str
    trigger: str
    status: str = "PENDING" # PENDING, PROCESSING, COMPLETED, FAILED
    createdAt: datetime
    processedAt: Optional[datetime] = None
    error: Optional[str] = None
