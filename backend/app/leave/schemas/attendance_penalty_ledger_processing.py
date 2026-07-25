from pydantic import BaseModel
from typing import Optional

class AttendancePenaltyLedgerProcessingCreate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class AttendancePenaltyLedgerProcessingUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class AttendancePenaltyLedgerProcessingResponse(AttendancePenaltyLedgerProcessingCreate):
    id: str
