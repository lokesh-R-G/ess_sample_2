from pydantic import BaseModel
from typing import Optional

class OrganizationCreate(BaseModel):
    name: str

class OrganizationUpdate(BaseModel):
    name: Optional[str] = None

class OrganizationResponse(OrganizationCreate):
    id: str
