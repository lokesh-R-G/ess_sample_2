from pydantic import BaseModel
from typing import Optional

class NumberSeryCreate(BaseModel):
    pass

class NumberSeryUpdate(BaseModel):
    pass

class NumberSeryResponse(NumberSeryCreate):
    id: str
