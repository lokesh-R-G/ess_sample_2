from pydantic import BaseModel
from typing import Optional

class PayrollRunCreate(BaseModel):
    status: Optional[str] = "Active"

class PayrollRunUpdate(BaseModel):
    status: Optional[str] = None

class PayrollRunResponse(PayrollRunCreate):
    id: str
