from pydantic import BaseModel
from typing import Optional

class PayslipTemplateCreate(BaseModel):
    pass

class PayslipTemplateUpdate(BaseModel):
    pass

class PayslipTemplateResponse(PayslipTemplateCreate):
    id: str
