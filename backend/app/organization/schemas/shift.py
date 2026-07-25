from pydantic import BaseModel
from typing import Optional

class ShiftCreate(BaseModel):
    name: str

class ShiftUpdate(BaseModel):
    name: Optional[str] = None

class ShiftResponse(ShiftCreate):
    id: str
