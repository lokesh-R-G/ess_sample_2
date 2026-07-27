from pydantic import BaseModel
from typing import Optional

class PayrollRunCreate(BaseModel):
    pass

class PayrollRunUpdate(BaseModel):
    pass

class PayrollRunResponse(PayrollRunCreate):
    id: str
