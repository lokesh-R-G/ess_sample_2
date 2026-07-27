from pydantic import BaseModel
from typing import Optional

class AssetHistoryCreate(BaseModel):
    pass

class AssetHistoryUpdate(BaseModel):
    pass

class AssetHistoryResponse(AssetHistoryCreate):
    id: str
