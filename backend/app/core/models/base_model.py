from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class BaseDBModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    companyId: Optional[str] = None
    status: str = "Active"
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    createdBy: Optional[str] = None
    updatedBy: Optional[str] = None
    isDeleted: bool = False
    deletedAt: Optional[datetime] = None
    deletedBy: Optional[str] = None
