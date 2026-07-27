from pydantic import BaseModel
from typing import Optional

class AuditLogCreate(BaseModel):
    pass

class AuditLogUpdate(BaseModel):
    pass

class AuditLogResponse(AuditLogCreate):
    id: str
