from pydantic import BaseModel, Field
from typing import Optional

class CompanyCreate(BaseModel):
    name: str

class CompanyUpdate(BaseModel):
    name: Optional[str] = None

class CompanyResponse(CompanyCreate):
    id: str = Field(alias="_id")
