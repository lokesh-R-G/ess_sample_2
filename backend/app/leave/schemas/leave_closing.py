from pydantic import BaseModel
from typing import Optional

class LeaveClosingCreate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class LeaveClosingUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class LeaveClosingResponse(LeaveClosingCreate):
    id: str
