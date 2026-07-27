from pydantic import BaseModel
from typing import Optional

class CostCenterCreate(BaseModel):
    pass

class CostCenterUpdate(BaseModel):
    pass

class CostCenterResponse(CostCenterCreate):
    id: str
