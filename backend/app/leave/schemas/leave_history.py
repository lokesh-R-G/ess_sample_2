from pydantic import BaseModel
from typing import Optional

class LeaveHistoryCreate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class LeaveHistoryUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class LeaveHistoryResponse(LeaveHistoryCreate):
    id: str
