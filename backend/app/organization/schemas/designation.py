from pydantic import BaseModel, Field
from typing import Optional

class DesignationCreate(BaseModel):
    name: str

class DesignationUpdate(BaseModel):
    name: Optional[str] = None

class DesignationResponse(DesignationCreate):
    id: str = Field(alias="_id")
