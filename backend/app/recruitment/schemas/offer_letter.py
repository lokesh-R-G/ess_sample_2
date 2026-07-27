from pydantic import BaseModel
from typing import Optional

class OfferLetterCreate(BaseModel):
    pass

class OfferLetterUpdate(BaseModel):
    pass

class OfferLetterResponse(OfferLetterCreate):
    id: str
