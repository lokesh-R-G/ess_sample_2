from pydantic import BaseModel
from typing import Optional

class LoanTypeCreate(BaseModel):
    pass

class LoanTypeUpdate(BaseModel):
    pass

class LoanTypeResponse(LoanTypeCreate):
    id: str
