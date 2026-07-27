from pydantic import BaseModel
from typing import Optional

class LoginAuditLogCreate(BaseModel):
    pass

class LoginAuditLogUpdate(BaseModel):
    pass

class LoginAuditLogResponse(LoginAuditLogCreate):
    id: str
