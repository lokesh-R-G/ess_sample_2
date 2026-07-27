from pydantic import BaseModel
from typing import Optional

class JobOpeningCreate(BaseModel):
    pass

class JobOpeningUpdate(BaseModel):
    pass

class JobOpeningResponse(JobOpeningCreate):
    id: str
