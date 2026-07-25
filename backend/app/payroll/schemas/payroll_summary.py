from pydantic import BaseModel
from typing import Optional

class PayrollSummaryCreate(BaseModel):
    status: Optional[str] = "Active"

class PayrollSummaryUpdate(BaseModel):
    status: Optional[str] = None

class PayrollSummaryResponse(PayrollSummaryCreate):
    id: str
