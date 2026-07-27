from pydantic import BaseModel
from typing import Optional

class PayrollEmployeeCreate(BaseModel):
    pass

class PayrollEmployeeUpdate(BaseModel):
    pass

class PayrollEmployeeResponse(PayrollEmployeeCreate):
    id: str
