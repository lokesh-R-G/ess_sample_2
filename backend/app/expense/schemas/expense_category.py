from pydantic import BaseModel
from typing import Optional

class ExpenseCategoryCreate(BaseModel):
    pass

class ExpenseCategoryUpdate(BaseModel):
    pass

class ExpenseCategoryResponse(ExpenseCategoryCreate):
    id: str
