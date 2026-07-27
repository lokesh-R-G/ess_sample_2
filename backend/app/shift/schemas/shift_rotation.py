from pydantic import BaseModel
from typing import Optional

class ShiftRotationCreate(BaseModel):
    pass

class ShiftRotationUpdate(BaseModel):
    pass

class ShiftRotationResponse(ShiftRotationCreate):
    id: str
