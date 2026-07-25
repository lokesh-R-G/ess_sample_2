from pydantic import BaseModel
from typing import Optional

class LeaveSummaryCreate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class LeaveSummaryUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class LeaveSummaryResponse(LeaveSummaryCreate):
    id: str
