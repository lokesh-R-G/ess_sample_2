from pydantic import BaseModel
from typing import Optional

class CostCenterCreate(BaseModel):
    name: Optional[str] = None

class CostCenterUpdate(BaseModel):
    status: Optional[str] = None

class CostCenterResponse(CostCenterCreate):
    id: str
