from pydantic import BaseModel
from typing import Optional

class PayslipCreate(BaseModel):
    status: Optional[str] = "Active"

class PayslipUpdate(BaseModel):
    status: Optional[str] = None

class PayslipResponse(PayslipCreate):
    id: str
