from pydantic import BaseModel
from typing import Optional

class CtcTemplateCreate(BaseModel):
    pass

class CtcTemplateUpdate(BaseModel):
    pass

class CtcTemplateResponse(CtcTemplateCreate):
    id: str
