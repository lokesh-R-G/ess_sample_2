from __future__ import annotations

from datetime import datetime
# Updated role typing to support any DB‑driven role while preserving legacy literals
from typing import Literal, Annotated, Any


from pydantic import BaseModel, Field, ConfigDict


# RoleType is now a simple string to accommodate any role stored in DB
RoleType = str



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
    employeeId: str | None = None
    employeeCode: str | None = None
    role: RoleType # Legacy fallback
    roleId: str | None = None
    firstLogin: bool
    mustChangePassword: bool = False



class UserResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    empId: str
    role: RoleType
    firstLogin: bool
    companyId: str | None = None
    branchId: str | None = None
    departmentId: str | None = None
    designationId: str | None = None
    managerId: str | None = None
    roleId: str | None = None


class Company(BaseModel):
    id: str | None = Field(default=None, alias="_id")
    name: str
    code: str | None = None
    createdAt: datetime | None = None
    updatedAt: datetime | None = None


class Branch(BaseModel):
    id: str | None = Field(default=None, alias="_id")
    companyId: str
    name: str
    code: str | None = None
    location: str | None = None
    createdAt: datetime | None = None
    updatedAt: datetime | None = None


class Department(BaseModel):
    id: str | None = Field(default=None, alias="_id")
    companyId: str
    name: str
    code: str | None = None
    createdAt: datetime | None = None
    updatedAt: datetime | None = None


class Designation(BaseModel):
    id: str | None = Field(default=None, alias="_id")
    companyId: str
    departmentId: str | None = None
    name: str
    code: str | None = None
    createdAt: datetime | None = None
    updatedAt: datetime | None = None


class Workflow(BaseModel):
    id: str | None = Field(default=None, alias="_id")
    workflowType: str
    entityId: str
    employeeId: str
    currentApproverId: str | None = None
    status: Literal["PENDING", "APPROVED", "REJECTED", "RETURNED"] = "PENDING"
    createdAt: datetime | None = None
    updatedAt: datetime | None = None


class WorkflowAction(BaseModel):
    id: str | None = Field(default=None, alias="_id")
    workflowId: str
    action: Literal["APPROVED", "REJECTED", "RETURNED"]
    actedBy: str
    remarks: str | None = None
    actedAt: datetime | None = None


class MissPunchRequest(BaseModel):
    id: str | None = Field(default=None, alias="_id")
    employeeId: str
    attendanceDate: str
    requestType: Literal["MISSING_IN", "MISSING_OUT"]
    requestedTime: str
    reason: str
    workflowId: str | None = None
    createdAt: datetime | None = None
    updatedAt: datetime | None = None


class AttendanceAuditLog(BaseModel):
    id: str | None = Field(default=None, alias="_id")
    empId: str
    date: str
    oldAttendance: dict | None = None
    newAttendance: dict | None = None
    approverId: str
    reason: str
    timestamp: datetime | None = None


class SyncRequest(BaseModel):
    fromDate: datetime | None = None
    toDate: datetime | None = None


class SyncResponse(BaseModel):
    rawInserted: int
    rawUpdated: int
    rawMatched: int = 0
    attendanceUpserted: int
    dateRange: dict[str, str | None]


class AttendancePolicy(BaseModel):
    shiftStartTime: str = "10:00:00"
    shiftEndTime: str = "18:30:00"
    saturdayShiftEndTime: str = "17:30:00"
    graceMinutes: int = 3
    lateStartMinute: int = 4
    lateEndMinute: int = 15
    latePermissionStartMinute: int = 16
    latePermissionEndMinute: int = 30
    halfDayCutoffTime: str = "10:30:00"
    monthlyPermissionHours: float = 1.0
    lateHalfDayThreshold: int = 4
    lateFullDayThreshold: int = 6
    lateIncrementThreshold: int = 4
    lopHalfDayHours: float = 4.0
    lopFullDayHours: float = 8.0

class SchedulerJobConfig(BaseModel):
    id: str | None = Field(default=None, alias="_id")
    jobKey: str  # ESSL_SHORT_SYNC, ESSL_RECOVERY_SYNC, ATTENDANCE_CALCULATION
    enabled: bool = True
    frequencyMinutes: int
    lookbackDays: int
    timezone: str = "Asia/Kolkata"
    createdAt: datetime | None = None
    updatedAt: datetime | None = None
    updatedBy: str | None = None
