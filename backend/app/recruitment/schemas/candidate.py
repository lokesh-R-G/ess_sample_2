from pydantic import BaseModel
from typing import Optional

class CandidateCreate(BaseModel):
    pass

class CandidateUpdate(BaseModel):
    pass

class CandidateResponse(CandidateCreate):
    id: str
