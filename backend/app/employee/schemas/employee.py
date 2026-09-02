from pydantic import BaseModel
from typing import Optional

class EmployeeCreate(BaseModel):
    employeeCode: Optional[str] = None

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
