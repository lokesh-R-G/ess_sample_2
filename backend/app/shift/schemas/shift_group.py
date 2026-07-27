from pydantic import BaseModel
from typing import Optional

class ShiftGroupCreate(BaseModel):
    pass

class ShiftGroupUpdate(BaseModel):
    pass

class ShiftGroupResponse(ShiftGroupCreate):
    id: str
