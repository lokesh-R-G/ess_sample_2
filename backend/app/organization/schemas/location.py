from pydantic import BaseModel, Field
from typing import Optional

class LocationCreate(BaseModel):
    pass

class LocationUpdate(BaseModel):
    pass

class LocationResponse(LocationCreate):
    id: str = Field(alias="_id")
