from pydantic import BaseModel
from typing import Optional

class MonthlyDeductionLedgerCreate(BaseModel):
    status: Optional[str] = "Active"

class MonthlyDeductionLedgerUpdate(BaseModel):
    status: Optional[str] = None

class MonthlyDeductionLedgerResponse(MonthlyDeductionLedgerCreate):
    id: str
