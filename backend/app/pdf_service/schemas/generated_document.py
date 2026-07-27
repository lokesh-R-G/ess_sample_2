from pydantic import BaseModel
from typing import Optional

class GeneratedDocumentCreate(BaseModel):
    pass

class GeneratedDocumentUpdate(BaseModel):
    pass

class GeneratedDocumentResponse(GeneratedDocumentCreate):
    id: str
