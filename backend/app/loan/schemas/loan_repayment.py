from pydantic import BaseModel
from typing import Optional

class LoanRepaymentCreate(BaseModel):
    pass

class LoanRepaymentUpdate(BaseModel):
    pass

class LoanRepaymentResponse(LoanRepaymentCreate):
    id: str
