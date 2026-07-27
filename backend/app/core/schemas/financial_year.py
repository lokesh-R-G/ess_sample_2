from pydantic import BaseModel
from typing import Optional

class FinancialYearCreate(BaseModel):
    pass

class FinancialYearUpdate(BaseModel):
    pass

class FinancialYearResponse(FinancialYearCreate):
    id: str
