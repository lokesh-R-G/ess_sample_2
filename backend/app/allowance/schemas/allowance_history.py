from pydantic import BaseModel
from typing import Optional

class AllowanceHistoryCreate(BaseModel):
    pass

class AllowanceHistoryUpdate(BaseModel):
    pass

class AllowanceHistoryResponse(AllowanceHistoryCreate):
    id: str
