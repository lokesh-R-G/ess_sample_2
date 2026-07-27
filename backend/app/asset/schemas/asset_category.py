from pydantic import BaseModel
from typing import Optional

class AssetCategoryCreate(BaseModel):
    pass

class AssetCategoryUpdate(BaseModel):
    pass

class AssetCategoryResponse(AssetCategoryCreate):
    id: str
