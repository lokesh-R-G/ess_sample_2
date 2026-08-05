from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class DesignationModel(BaseModel):
    model_config = ConfigDict(extra="allow")
    
    id: Optional[str] = Field(default=None, alias="_id")
    companyId: Optional[str] = None
    departmentId: Optional[str] = None
    departmentName: Optional[str] = None
    code: Optional[str] = None
    name: Optional[str] = None
    status: str = "Active"
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    createdBy: Optional[str] = None
    updatedBy: Optional[str] = None
    deletedAt: Optional[datetime] = None
    deletedBy: Optional[str] = None
