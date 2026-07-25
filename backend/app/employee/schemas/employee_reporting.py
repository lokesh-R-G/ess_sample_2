from pydantic import BaseModel
from typing import Optional

class EmployeeReportingCreate(BaseModel):
    employeeId: str

class EmployeeReportingUpdate(BaseModel):
    status: Optional[str] = None

class EmployeeReportingResponse(EmployeeReportingCreate):
    id: str
