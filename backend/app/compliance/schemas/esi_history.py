from pydantic import BaseModel
from typing import Optional

class EsiHistoryCreate(BaseModel):
    pass

class EsiHistoryUpdate(BaseModel):
    pass

class EsiHistoryResponse(EsiHistoryCreate):
    id: str
