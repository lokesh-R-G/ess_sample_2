from pydantic import BaseModel
from typing import Optional, Dict, Any

class LeaveConversionLedgerCreate(BaseModel):
    status: Optional[str] = None

class LeaveConversionLedgerUpdate(BaseModel):
    status: Optional[str] = None

class LeaveConversionLedgerResponse(LeaveConversionLedgerCreate):
    id: str
