from pydantic import BaseModel
from typing import Optional

class PfCeilingConfigCreate(BaseModel):
    status: Optional[str] = "Active"

class PfCeilingConfigUpdate(BaseModel):
    status: Optional[str] = None

class PfCeilingConfigResponse(PfCeilingConfigCreate):
    id: str
