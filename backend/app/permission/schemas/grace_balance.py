from pydantic import BaseModel
from typing import Optional, Dict, Any

class GraceBalanceCreate(BaseModel):
    status: Optional[str] = None

class GraceBalanceUpdate(BaseModel):
    status: Optional[str] = None

class GraceBalanceResponse(GraceBalanceCreate):
    id: str
