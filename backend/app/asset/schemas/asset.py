from pydantic import BaseModel
from typing import Optional

class AssetCreate(BaseModel):
    pass

class AssetUpdate(BaseModel):
    pass

class AssetResponse(AssetCreate):
    id: str
