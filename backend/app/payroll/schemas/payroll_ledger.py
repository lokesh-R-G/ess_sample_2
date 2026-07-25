from pydantic import BaseModel
from typing import Optional

class PayrollLedgerCreate(BaseModel):
    status: Optional[str] = "Active"

class PayrollLedgerUpdate(BaseModel):
    status: Optional[str] = None

class PayrollLedgerResponse(PayrollLedgerCreate):
    id: str
