from pydantic import BaseModel
from typing import Optional

class PayrollCycleCreate(BaseModel):
    pass

class PayrollCycleUpdate(BaseModel):
    pass

class PayrollCycleResponse(PayrollCycleCreate):
    id: str
