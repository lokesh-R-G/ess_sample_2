from pydantic import BaseModel
from typing import Optional

class BusinessUnitCreate(BaseModel):
    pass

class BusinessUnitUpdate(BaseModel):
    pass

class BusinessUnitResponse(BusinessUnitCreate):
    id: str
