from pydantic import BaseModel
from typing import Optional

class IncomeTaxSlabCreate(BaseModel):
    pass

class IncomeTaxSlabUpdate(BaseModel):
    pass

class IncomeTaxSlabResponse(IncomeTaxSlabCreate):
    id: str
