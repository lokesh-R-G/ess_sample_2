from pydantic import BaseModel
from typing import Optional

class EmployeeCreate(BaseModel):
    employeeId: str
    employeeCode: str = ""

class EmployeeUpdate(BaseModel):
    status: Optional[str] = None
    systemAccessEnabled: Optional[bool] = None
    authUserId: Optional[str] = None
    essStatus: Optional[str] = None
    employeeCode: Optional[str] = None

class EmployeeResponse(EmployeeCreate):
    id: str
    systemAccessEnabled: bool
    authUserId: Optional[str] = None
    essStatus: str
    status: str
