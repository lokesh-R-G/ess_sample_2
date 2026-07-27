from pydantic import BaseModel
from typing import Optional

class ShiftDefinitionCreate(BaseModel):
    pass

class ShiftDefinitionUpdate(BaseModel):
    pass

class ShiftDefinitionResponse(ShiftDefinitionCreate):
    id: str
