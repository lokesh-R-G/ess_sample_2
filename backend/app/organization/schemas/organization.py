from pydantic import BaseModel, Field
from typing import Optional

class OrganizationCreate(BaseModel):
    name: str

class OrganizationUpdate(BaseModel):
    name: Optional[str] = None

class OrganizationResponse(OrganizationCreate):
    id: str = Field(alias="_id")
