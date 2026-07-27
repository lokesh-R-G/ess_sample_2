from pydantic import BaseModel
from typing import Optional

class LocationCreate(BaseModel):
    pass

class LocationUpdate(BaseModel):
    pass

class LocationResponse(LocationCreate):
    id: str
