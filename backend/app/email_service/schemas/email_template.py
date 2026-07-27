from pydantic import BaseModel
from typing import Optional

class EmailTemplateCreate(BaseModel):
    pass

class EmailTemplateUpdate(BaseModel):
    pass

class EmailTemplateResponse(EmailTemplateCreate):
    id: str
