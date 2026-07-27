from pydantic import BaseModel
from typing import Optional

class EmployeeCertificationCreate(BaseModel):
    pass

class EmployeeCertificationUpdate(BaseModel):
    pass

class EmployeeCertificationResponse(EmployeeCertificationCreate):
    id: str
