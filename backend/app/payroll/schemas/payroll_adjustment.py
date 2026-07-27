from pydantic import BaseModel
from typing import Optional

class PayrollAdjustmentCreate(BaseModel):
    pass

class PayrollAdjustmentUpdate(BaseModel):
    pass

class PayrollAdjustmentResponse(PayrollAdjustmentCreate):
    id: str
