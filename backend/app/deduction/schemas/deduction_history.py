from pydantic import BaseModel
from typing import Optional

class DeductionHistoryCreate(BaseModel):
    pass

class DeductionHistoryUpdate(BaseModel):
    pass

class DeductionHistoryResponse(DeductionHistoryCreate):
    id: str
