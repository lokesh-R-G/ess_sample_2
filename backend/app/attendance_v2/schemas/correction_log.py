from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel

class CorrectionLogCreate(BaseModel):
    entityType: str
    entityCode: str
    originalVersion: int
    effectiveFrom: datetime
    effectiveTo: Optional[datetime] = None
    changedFields: Dict[str, Any]
    reason: str

class CorrectionLogResponse(CorrectionLogCreate):
    id: str
    correctionCode: str
    correctionVersion: int
    createdAt: Optional[datetime] = None
    createdBy: Optional[str] = None

class PaginatedCorrectionLogResponse(BaseModel):
    data: List[CorrectionLogResponse]
    total: int
    page: int = 1
    pageSize: int = 100
    totalPages: int = 1
