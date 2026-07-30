from pydantic import BaseModel, Field
from typing import Optional

class CostCenterCreate(BaseModel):
    pass

class CostCenterUpdate(BaseModel):
    pass

class CostCenterResponse(CostCenterCreate):
    id: str = Field(alias="_id")
