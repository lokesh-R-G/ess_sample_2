from pydantic import BaseModel
from typing import Optional

class ManualDeductionCreate(BaseModel):
    status: Optional[str] = "Active"

class ManualDeductionUpdate(BaseModel):
    status: Optional[str] = None

class ManualDeductionResponse(ManualDeductionCreate):
    id: str
