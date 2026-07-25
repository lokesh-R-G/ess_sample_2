from pydantic import BaseModel
from typing import Optional

class DesignationCreate(BaseModel):
    name: str

class DesignationUpdate(BaseModel):
    name: Optional[str] = None

class DesignationResponse(DesignationCreate):
    id: str
