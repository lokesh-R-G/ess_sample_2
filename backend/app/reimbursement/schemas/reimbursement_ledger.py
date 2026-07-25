from pydantic import BaseModel
from typing import Optional

class ReimbursementLedgerCreate(BaseModel):
    status: Optional[str] = "Active"

class ReimbursementLedgerUpdate(BaseModel):
    status: Optional[str] = None

class ReimbursementLedgerResponse(ReimbursementLedgerCreate):
    id: str
