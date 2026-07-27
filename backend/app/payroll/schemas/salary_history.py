from pydantic import BaseModel
from typing import Optional

class SalaryHistoryCreate(BaseModel):
    pass

class SalaryHistoryUpdate(BaseModel):
    pass

class SalaryHistoryResponse(SalaryHistoryCreate):
    id: str
