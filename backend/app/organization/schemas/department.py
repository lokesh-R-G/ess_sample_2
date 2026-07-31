from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

class DepartmentCreate(BaseModel):
    companyId: str
    name: str

class DepartmentUpdate(BaseModel):
    companyId: Optional[str] = None
    name: Optional[str] = None

class DepartmentResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: str = Field(serialization_alias="_id")
    companyId: str
    name: str
    status: Optional[str] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
