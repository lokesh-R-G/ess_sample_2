from pydantic import BaseModel
from typing import Optional

class CompOffBalanceCreate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class CompOffBalanceUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class CompOffBalanceResponse(CompOffBalanceCreate):
    id: str
