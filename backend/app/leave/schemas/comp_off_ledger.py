from pydantic import BaseModel
from typing import Optional

class CompOffLedgerCreate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class CompOffLedgerUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class CompOffLedgerResponse(CompOffLedgerCreate):
    id: str
