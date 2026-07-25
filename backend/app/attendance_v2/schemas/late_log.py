from pydantic import BaseModel
from typing import Optional

class LateLogCreate(BaseModel):
    name: Optional[str] = None

class LateLogUpdate(BaseModel):
    status: Optional[str] = None

class LateLogResponse(LateLogCreate):
    id: str
