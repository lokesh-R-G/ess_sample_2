from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class RoleModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    roleId: str
    name: str
    description: str = ""
    isSystemRole: bool = True
    isActive: bool = True
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

class PermissionModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    permissionCode: str
    module: str
    action: str
    description: str = ""
    isActive: bool = True

class RolePermissionModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    roleId: str
    permissionCode: str
    scope: str # SELF, TEAM, BRANCH, COMPANY, GLOBAL
    isActive: bool = True
