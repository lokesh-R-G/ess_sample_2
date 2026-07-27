from pydantic import BaseModel
from typing import Optional

class EmployeeDocumentCreate(BaseModel):
    pass

class EmployeeDocumentUpdate(BaseModel):
    pass

class EmployeeDocumentResponse(EmployeeDocumentCreate):
    id: str
