from pydantic import BaseModel
from typing import Optional

class EmployeeCreate(BaseModel):
    # Empty schema, the backend generates everything on creation
    pass

class EmployeeUpdate(BaseModel):
    status: Optional[str] = None
    systemAccessEnabled: Optional[bool] = None
    authUserId: Optional[str] = None
    essStatus: Optional[str] = None
    employeeCode: Optional[str] = None

class EmployeeResponse(BaseModel):
    id: str
    employeeId: str
    employeeCode: Optional[str] = None
    systemAccessEnabled: bool
    authUserId: Optional[str] = None
    essStatus: str
    status: str
