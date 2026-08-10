from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class CorrectionLogModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    correctionCode: str
    entityType: str # e.g. 'AttendancePolicy', 'Shift'
    entityCode: str
    originalVersion: int
    correctionVersion: int
    effectiveFrom: datetime
    effectiveTo: Optional[datetime] = None
    changedFields: Dict[str, Any]
    reason: str
    
    # Audit
    createdAt: Optional[datetime] = None
    createdBy: Optional[str] = None
