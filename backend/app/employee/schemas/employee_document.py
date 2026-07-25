from pydantic import BaseModel
from typing import Optional

class EmployeeDocumentCreate(BaseModel):
    employeeId: str

class EmployeeDocumentUpdate(BaseModel):
    status: Optional[str] = None

class EmployeeDocumentResponse(EmployeeDocumentCreate):
    id: str
