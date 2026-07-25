from pydantic import BaseModel
from typing import Optional

class LeavePolicyHistoryCreate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class LeavePolicyHistoryUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class LeavePolicyHistoryResponse(LeavePolicyHistoryCreate):
    id: str
