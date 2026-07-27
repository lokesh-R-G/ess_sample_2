from pydantic import BaseModel
from typing import Optional

class PayrollPolicyCreate(BaseModel):
    pass

class PayrollPolicyUpdate(BaseModel):
    pass

class PayrollPolicyResponse(PayrollPolicyCreate):
    id: str
