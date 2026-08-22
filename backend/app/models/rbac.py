from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, ConfigDict

# Role model
class Role(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str | None = Field(default=None, alias="_id")
    roleId: str
    name: str
    description: str | None = None
    isActive: bool = True
    createdAt: datetime | None = None
    updatedAt: datetime | None = None
    version: int = 1

# Permission model
class Permission(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str | None = Field(default=None, alias="_id")
    permissionId: str
    name: str
    description: str | None = None
    module: str
    action: str
    isActive: bool = True
    createdAt: datetime | None = None
    updatedAt: datetime | None = None
    version: int = 1

# Role-Permission mapping
class RolePermission(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str | None = Field(default=None, alias="_id")
    roleId: str
    permissionId: str
    scope: Literal["SELF", "TEAM", "BRANCH", "COMPANY", "GLOBAL"]
    isActive: bool = True
    version: int = 1
    effectiveFrom: datetime | None = None
    effectiveTo: datetime | None = None
    createdAt: datetime | None = None
    updatedAt: datetime | None = None
    createdBy: str | None = None
    updatedBy: str | None = None

# Role-Permission history for versioning
class RolePermissionHistory(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str | None = Field(default=None, alias="_id")
    roleId: str
    permissionId: str
    previousScope: Literal["SELF", "TEAM", "BRANCH", "COMPANY", "GLOBAL"] | None = None
    newScope: Literal["SELF", "TEAM", "BRANCH", "COMPANY", "GLOBAL"] | None = None
    previousState: bool | None = None
    newState: bool | None = None
    changeType: Literal["ADD", "REMOVE", "UPDATE"]
    version: int
    changedBy: str | None = None
    changedAt: datetime = Field(default_factory=datetime.utcnow)
    reason: str | None = None
