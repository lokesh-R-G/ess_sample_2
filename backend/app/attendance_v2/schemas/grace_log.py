from pydantic import BaseModel
from typing import Optional

class GraceLogCreate(BaseModel):
    name: Optional[str] = None

class GraceLogUpdate(BaseModel):
    status: Optional[str] = None

class GraceLogResponse(GraceLogCreate):
    id: str
