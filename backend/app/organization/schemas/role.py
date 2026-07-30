from pydantic import BaseModel, Field
from typing import Optional

class RoleCreate(BaseModel):
    name: str

class RoleUpdate(BaseModel):
    name: Optional[str] = None

class RoleResponse(RoleCreate):
    id: str = Field(alias="_id")
