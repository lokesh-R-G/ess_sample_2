from pydantic import BaseModel
from typing import Optional

class EmployeeExperienceCreate(BaseModel):
    pass

class EmployeeExperienceUpdate(BaseModel):
    pass

class EmployeeExperienceResponse(EmployeeExperienceCreate):
    id: str
