from pydantic import BaseModel
from typing import Optional

class WorkflowHistoryCreate(BaseModel):
    pass

class WorkflowHistoryUpdate(BaseModel):
    pass

class WorkflowHistoryResponse(WorkflowHistoryCreate):
    id: str
