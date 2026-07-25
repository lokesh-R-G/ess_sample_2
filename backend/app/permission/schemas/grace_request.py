from pydantic import BaseModel
from typing import Optional

class GraceRequestCreate(BaseModel):
    name: Optional[str] = None

class GraceRequestUpdate(BaseModel):
    status: Optional[str] = None

class GraceRequestResponse(GraceRequestCreate):
    id: str
