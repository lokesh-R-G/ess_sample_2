from pydantic import BaseModel
from typing import Optional

class ExpenseTypeConfigCreate(BaseModel):
    status: Optional[str] = "Active"

class ExpenseTypeConfigUpdate(BaseModel):
    status: Optional[str] = None

class ExpenseTypeConfigResponse(ExpenseTypeConfigCreate):
    id: str
