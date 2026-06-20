from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, ConfigDict


RoleType = Literal["Employee", "Admin"]


class LoginRequest(BaseModel):
    empId: str = Field(min_length=1)
    password: str = Field(min_length=1)


class ChangePasswordRequest(BaseModel):
    currentPassword: str = Field(min_length=1)
    newPassword: str = Field(min_length=8)


class TokenResponse(BaseModel):
    accessToken: str
    tokenType: str = "bearer"
    empId: str
    role: RoleType
    firstLogin: bool
    mustChangePassword: bool = False


class UserResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    empId: str
    role: RoleType
    firstLogin: bool


class SyncRequest(BaseModel):
    fromDate: datetime | None = None
    toDate: datetime | None = None


class SyncResponse(BaseModel):
    rawInserted: int
    rawUpdated: int
    attendanceUpserted: int
    dateRange: dict[str, str | None]
