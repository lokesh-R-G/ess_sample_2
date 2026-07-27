from pydantic import BaseModel
from typing import Optional

class SalaryRevisionCreate(BaseModel):
    pass

class SalaryRevisionUpdate(BaseModel):
    pass

class SalaryRevisionResponse(SalaryRevisionCreate):
    id: str
