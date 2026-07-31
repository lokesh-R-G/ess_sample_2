from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

class DesignationCreate(BaseModel):
    companyId: str
    departmentId: str
    name: str

class DesignationUpdate(BaseModel):
    companyId: Optional[str] = None
    departmentId: Optional[str] = None
    name: Optional[str] = None

class DesignationResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: str = Field(serialization_alias="_id")
    companyId: str
    departmentId: str
    name: str
    status: Optional[str] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
