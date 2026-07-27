from pydantic import BaseModel
from typing import Optional

class EmployeeReimbursementCreate(BaseModel):
    pass

class EmployeeReimbursementUpdate(BaseModel):
    pass

class EmployeeReimbursementResponse(EmployeeReimbursementCreate):
    id: str
