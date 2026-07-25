from pydantic import BaseModel
from typing import Optional

class PayrollProcessingRuleCreate(BaseModel):
    status: Optional[str] = "Active"

class PayrollProcessingRuleUpdate(BaseModel):
    status: Optional[str] = None

class PayrollProcessingRuleResponse(PayrollProcessingRuleCreate):
    id: str
