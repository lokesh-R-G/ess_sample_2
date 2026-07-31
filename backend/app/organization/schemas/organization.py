from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

class OrganizationCreate(BaseModel):
    name: str
    domain: Optional[str] = None

class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    domain: Optional[str] = None

class OrganizationResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: str = Field(serialization_alias="_id")
    name: str
    domain: Optional[str] = None
    status: Optional[str] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
