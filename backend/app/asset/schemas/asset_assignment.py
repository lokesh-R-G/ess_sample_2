from pydantic import BaseModel
from typing import Optional

class AssetAssignmentCreate(BaseModel):
    pass

class AssetAssignmentUpdate(BaseModel):
    pass

class AssetAssignmentResponse(AssetAssignmentCreate):
    id: str
