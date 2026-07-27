from pydantic import BaseModel
from typing import Optional

class DocumentTemplateCreate(BaseModel):
    pass

class DocumentTemplateUpdate(BaseModel):
    pass

class DocumentTemplateResponse(DocumentTemplateCreate):
    id: str
