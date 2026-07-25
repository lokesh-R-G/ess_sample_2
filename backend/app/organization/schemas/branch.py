from pydantic import BaseModel
from typing import Optional

class BranchCreate(BaseModel):
    name: str

class BranchUpdate(BaseModel):
    name: Optional[str] = None

class BranchResponse(BranchCreate):
    id: str
