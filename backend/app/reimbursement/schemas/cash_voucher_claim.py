from pydantic import BaseModel
from typing import Optional

class CashVoucherClaimCreate(BaseModel):
    status: Optional[str] = "Active"

class CashVoucherClaimUpdate(BaseModel):
    status: Optional[str] = None

class CashVoucherClaimResponse(CashVoucherClaimCreate):
    id: str
