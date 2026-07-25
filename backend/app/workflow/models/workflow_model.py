from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class WorkflowModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    entityType: str
    entityId: str
    requesterId: str
    approverId: str
    status: str = "Pending"
    createdAt: datetime
    updatedAt: datetime
