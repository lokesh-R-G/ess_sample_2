from pydantic import BaseModel
from typing import Optional

class EmploymentHistoryCreate(BaseModel):
    employeeId: str

class EmploymentHistoryUpdate(BaseModel):
    status: Optional[str] = None

class EmploymentHistoryResponse(EmploymentHistoryCreate):
    id: str
