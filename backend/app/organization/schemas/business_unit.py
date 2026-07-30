from pydantic import BaseModel, Field
from typing import Optional

class BusinessUnitCreate(BaseModel):
    pass

class BusinessUnitUpdate(BaseModel):
    pass

class BusinessUnitResponse(BusinessUnitCreate):
    id: str = Field(alias="_id")
