from pydantic import BaseModel
from typing import Optional

class EsiConfigCreate(BaseModel):
    status: Optional[str] = "Active"

class EsiConfigUpdate(BaseModel):
    status: Optional[str] = None

class EsiConfigResponse(EsiConfigCreate):
    id: str
