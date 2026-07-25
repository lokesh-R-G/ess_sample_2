from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from ..core.config import get_settings


settings = get_settings()
client = AsyncIOMotorClient(settings.mongo_uri) if settings.mongo_uri else None


def get_database() -> AsyncIOMotorDatabase:
    if client is None:
        raise RuntimeError("MONGODB_URI is not configured")
    return client[settings.mongo_db_name]


async def init_indexes() -> None:
    db = get_database()
    await db.users.create_index([("empId", 1)], unique=True)
    # Ensure raw log de-duplication by fingerprint and by empId+timestamp
    await db.attendance_logs.create_index([("fingerprint", 1)], unique=True)
    await db.attendance_logs.create_index([("empId", 1), ("timestamp", 1)], unique=True)
    await db.attendance.create_index([("empId", 1), ("date", 1)], unique=True)
    await db.attendance.create_index([("empId", 1), ("date", -1)])
    
    # Organization Engine Indexes
    await db.companies.create_index([("organizationId", 1), ("name", 1)], unique=True, sparse=True)
    await db.branches.create_index([("companyId", 1), ("name", 1)], unique=True, sparse=True)
    await db.departments.create_index([("companyId", 1), ("name", 1)], unique=True, sparse=True)
    await db.designations.create_index([("departmentId", 1), ("name", 1)], unique=True, sparse=True)
    await db.roles.create_index([("companyId", 1), ("name", 1)], unique=True, sparse=True)
    await db.holidays.create_index([("companyId", 1), ("branchId", 1), ("date", 1)], unique=True, sparse=True)

    # Employee Engine Indexes
    await db.employees.create_index([("companyId", 1), ("empCode", 1)], unique=True, sparse=True)
    await db.employees.create_index([("email", 1)], unique=True, sparse=True)
    await db.employee_shift_assignments.create_index([("employeeId", 1), ("shiftId", 1), ("effectiveFrom", 1)], unique=True, sparse=True)
    await db.employee_role_assignments.create_index([("employeeId", 1), ("roleId", 1), ("effectiveFrom", 1)], unique=True, sparse=True)
    await db.employee_reportings.create_index([("employeeId", 1), ("managerId", 1), ("effectiveFrom", 1)], unique=True, sparse=True)
