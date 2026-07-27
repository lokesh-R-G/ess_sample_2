from pydantic import BaseModel
from typing import Optional

class PfHistoryCreate(BaseModel):
    pass

class PfHistoryUpdate(BaseModel):
    pass

class PfHistoryResponse(PfHistoryCreate):
    id: str
