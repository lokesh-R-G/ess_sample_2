from pydantic import BaseModel
from typing import Optional

class PayslipDeliveryLogCreate(BaseModel):
    pass

class PayslipDeliveryLogUpdate(BaseModel):
    pass

class PayslipDeliveryLogResponse(PayslipDeliveryLogCreate):
    id: str
