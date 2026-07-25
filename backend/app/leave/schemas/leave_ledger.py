from pydantic import BaseModel
from typing import Optional

class LeaveLedgerCreate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class LeaveLedgerUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class LeaveLedgerResponse(LeaveLedgerCreate):
    id: str
