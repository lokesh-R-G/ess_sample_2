from pydantic import BaseModel
from typing import Optional

class EmployeeExperienceCreate(BaseModel):
    employeeId: str

class EmployeeExperienceUpdate(BaseModel):
    status: Optional[str] = None

class EmployeeExperienceResponse(EmployeeExperienceCreate):
    id: str
