from pydantic import BaseModel
from typing import Optional

class LabourWelfareFundConfigCreate(BaseModel):
    status: Optional[str] = "Active"

class LabourWelfareFundConfigUpdate(BaseModel):
    status: Optional[str] = None

class LabourWelfareFundConfigResponse(LabourWelfareFundConfigCreate):
    id: str
