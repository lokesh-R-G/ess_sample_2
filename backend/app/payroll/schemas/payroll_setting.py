from pydantic import BaseModel
from typing import Optional

class PayrollSettingCreate(BaseModel):
    pass

class PayrollSettingUpdate(BaseModel):
    pass

class PayrollSettingResponse(PayrollSettingCreate):
    id: str
