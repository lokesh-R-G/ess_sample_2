from pydantic import BaseModel
from typing import Optional

class InterviewCreate(BaseModel):
    pass

class InterviewUpdate(BaseModel):
    pass

class InterviewResponse(InterviewCreate):
    id: str
