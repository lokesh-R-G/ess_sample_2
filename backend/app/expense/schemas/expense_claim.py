from pydantic import BaseModel
from typing import Optional

class ExpenseClaimCreate(BaseModel):
    pass

class ExpenseClaimUpdate(BaseModel):
    pass

class ExpenseClaimResponse(ExpenseClaimCreate):
    id: str
