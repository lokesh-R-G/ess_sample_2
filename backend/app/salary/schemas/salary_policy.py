from pydantic import BaseModel
from typing import Optional

class SalaryPolicyCreate(BaseModel):
    name: Optional[str] = None

class SalaryPolicyUpdate(BaseModel):
    status: Optional[str] = None

class SalaryPolicyResponse(SalaryPolicyCreate):
    id: str
