from pydantic import BaseModel
from typing import Optional

class CandidateDocumentCreate(BaseModel):
    pass

class CandidateDocumentUpdate(BaseModel):
    pass

class CandidateDocumentResponse(CandidateDocumentCreate):
    id: str
