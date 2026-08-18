from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class CashVoucherModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    claimId: str
    voucherDate: str  # YYYY-MM-DD
    expenseCategory: str
    vendorName: Optional[str] = None
    billNumber: Optional[str] = None
    
    claimedAmount: float
    calculatedAmount: float
    
    # Audit
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    createdBy: Optional[str] = None
    updatedBy: Optional[str] = None
