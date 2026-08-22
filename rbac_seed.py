import asyncio
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db.mongo import get_database

# Define roles
ROLES = [
    {"_id": "ROLE_EMPLOYEE", "roleId": "ROLE_EMPLOYEE", "name": "Employee", "description": "Standard employee role"},
    {"_id": "ROLE_MANAGER", "roleId": "ROLE_MANAGER", "name": "Manager", "description": "Managers can manage their team"},
    {"_id": "ROLE_HR", "roleId": "ROLE_HR", "name": "HR", "description": "Human Resources"},
    {"_id": "ROLE_ADMIN", "roleId": "ROLE_ADMIN", "name": "Admin", "description": "Company admin"},
    {"_id": "ROLE_ACCOUNTS", "roleId": "ROLE_ACCOUNTS", "name": "Accounts", "description": "Accounts department"},
    {"_id": "ROLE_ACCOUNTS_MD", "roleId": "ROLE_ACCOUNTS_MD", "name": "Accounts MD", "description": "Accounts MD role"},
    {"_id": "ROLE_SUPER_ADMIN", "roleId": "ROLE_SUPER_ADMIN", "name": "Super Admin", "description": "Global super admin"},
]

# Permission catalog – extend as needed.
PERMISSIONS = [
    {"permissionCode": "leave.read", "module": "leave", "action": "read", "description": "Read leave data"},
    {"permissionCode": "leave.apply", "module": "leave", "action": "apply", "description": "Apply for leave"},
    {"permissionCode": "leave.manage", "module": "leave", "action": "manage", "description": "Create / update / delete leave"},
    {"permissionCode": "leave.approve", "module": "leave", "action": "approve", "description": "Approve leave requests"},
    {"permissionCode": "attendance.read", "module": "attendance", "action": "read", "description": "Read attendance"},
    {"permissionCode": "attendance.manage", "module": "attendance", "action": "manage", "description": "Manage attendance records"},
    {"permissionCode": "payroll.read", "module": "payroll", "action": "read", "description": "Read payroll data"},
    {"permissionCode": "payroll.calculate", "module": "payroll", "action": "calculate", "description": "Calculate payroll"},
    {"permissionCode": "payroll.publish", "module": "payroll", "action": "publish", "description": "Publish payroll"},
    {"permissionCode": "organization.manage", "module": "organization", "action": "manage", "description": "Manage organization"},
    {"permissionCode": "policy.manage", "module": "policy", "action": "manage", "description": "Manage policies"},
]

# Role‑Permission mappings – Super Admin gets all permissions with GLOBAL scope.
ROLE_PERMISSIONS = []
for perm in PERMISSIONS:
    ROLE_PERMISSIONS.append({
        "roleId": "ROLE_SUPER_ADMIN",
        "permissionCode": perm["permissionCode"],
        "scope": "GLOBAL",
        "isActive": True,
    })

async def upsert_roles(db: AsyncIOMotorDatabase):
    for role in ROLES:
        await db["roles"].update_one(
            {"_id": role["_id"]},
            {"$setOnInsert": role},
            upsert=True,
        )

async def upsert_permissions(db: AsyncIOMotorDatabase):
    for perm in PERMISSIONS:
        await db["permissions"].update_one(
            {"permissionCode": perm["permissionCode"]},
            {"$setOnInsert": perm},
            upsert=True,
        )

async def upsert_role_permissions(db: AsyncIOMotorDatabase):
    for rp in ROLE_PERMISSIONS:
        await db["role_permissions"].update_one(
            {"roleId": rp["roleId"], "permissionCode": rp["permissionCode"]},
            {"$setOnInsert": rp},
            upsert=True,
        )

async def main():
    db = get_database()
    await upsert_roles(db)
    await upsert_permissions(db)
    await upsert_role_permissions(db)
    print("RBAC seed completed (idempotent).")
    # Report inserted / upserted document counts for verification
    role_count = await db["roles"].count_documents({})
    perm_count = await db["permissions"].count_documents({})
    rp_count = await db["role_permissions"].count_documents({})
    print(f"Roles count: {role_count}")
    print(f"Permissions count: {perm_count}")
    print(f"Role-Permissions count: {rp_count}")

if __name__ == "__main__":
    asyncio.run(main())
