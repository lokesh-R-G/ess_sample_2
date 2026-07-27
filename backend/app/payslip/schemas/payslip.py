from pydantic import BaseModel
from typing import Optional

class PayslipCreate(BaseModel):
    pass

class PayslipUpdate(BaseModel):
    pass

class PayslipResponse(PayslipCreate):
    id: str
