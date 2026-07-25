from pydantic import BaseModel
from typing import Optional

class DepartmentCreate(BaseModel):
    name: str

class DepartmentUpdate(BaseModel):
    name: Optional[str] = None

class DepartmentResponse(DepartmentCreate):
    id: str
