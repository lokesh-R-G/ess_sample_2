from pydantic import BaseModel
from typing import Optional

class LeaveCancellationCreate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class LeaveCancellationUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class LeaveCancellationResponse(LeaveCancellationCreate):
    id: str
