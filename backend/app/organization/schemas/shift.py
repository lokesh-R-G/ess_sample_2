from pydantic import BaseModel, Field
from typing import Optional

class ShiftCreate(BaseModel):
    name: str

class ShiftUpdate(BaseModel):
    name: Optional[str] = None

class ShiftResponse(ShiftCreate):
    id: str = Field(alias="_id")
