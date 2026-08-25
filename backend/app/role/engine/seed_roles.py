import logging
from datetime import datetime
from typing import List, Dict, Any

from motor.motor_asyncio import AsyncIOMotorDatabase

# Import canonical permissions
from app.permission.engine.seed_permissions import CANONICAL_PERMISSIONS

# Role definitions
ROLES: List[Dict[str, Any]] = [
    {"roleId": "employee", "name": "Employee", "description": "Standard employee role", "scope": "SELF"},
    {"roleId": "manager", "name": "Manager", "description": "Manager role", "scope": "TEAM"},
    {"roleId": "hr", "name": "HR", "description": "Human resources", "scope": "GLOBAL"},
    {"roleId": "admin", "name": "Admin", "description": "Administrator", "scope": "GLOBAL"},
    {"roleId": "accounts", "name": "Accounts", "description": "Accounts department", "scope": "COMPANY"},
    {"roleId": "accounts_md", "name": "Accounts MD", "description": "Accounts Managing Director", "scope": "GLOBAL"},
    {"roleId": "super_admin", "name": "Super Admin", "description": "Super administrator", "scope": "GLOBAL"},
]

# Permissions that a role must NOT receive (dash entries). Currently only Accounts has exclusions.
EXCLUDED_PERMISSIONS: Dict[str, List[str]] = {
    "accounts": [
        "payroll.calculate",
        "payroll.publish",
        "payroll.cycle.manage",
    ]
}

# Additional permissions excluded for accounts as per approved matrix
ACCOUNTS_EXCLUDED_PERMISSIONS: set = {
    "employee.read",
    "employee.manage",
    "leave.read",
    "leave.apply",
    "leave.manage",
    "leave.approve",
    "organization.read",
    "organization.manage",
    "policy.attendance.manage",
    "policy.leave.manage",
    "policy.reimbursement.manage",
    "policy.weekly_off.manage",
    "policy.shift.manage",
    "workflow.read",
    "workflow.manage",
    "workflow.approve",
    "essl.sync",
    "essl.recovery_sync",
    "attendance.sync",
    "scheduler.configure",
}


async def seed_roles_and_mappings(db: AsyncIOMotorDatabase | None = None) -> Dict[str, Any]:
    """Idempotently seed roles and role‑permission mappings.

    Returns a summary dict with counts of created roles, created mappings, history entries added, and any conflicts.
    """
    from app.db.mongo import get_database

    if db is None:
        db = get_database()

    created_roles = 0
    created_mappings = 0
    added_history = 0
    conflicts: List[Dict[str, Any]] = []

    # Seed roles
    for role in ROLES:
        now = datetime.utcnow()
        role_doc = {
            "roleId": role["roleId"],
            "name": role["name"],
            "description": role.get("description"),
            "isActive": True,
            "version": 1,
            "createdAt": now,
            "updatedAt": now,
        }
        existing = await db.roles.find_one({"roleId": role["roleId"]})
        if not existing:
            await db.roles.insert_one(role_doc)
            created_roles += 1
        # No update of existing role to keep idempotency.

    # Seed role_permission mappings
    for role in ROLES:
        role_id = role["roleId"]
        base_scope = role["scope"]
        for perm in CANONICAL_PERMISSIONS:
            perm_id = perm["permissionId"]
            # Skip excluded permissions for this role
            if role_id in EXCLUDED_PERMISSIONS and perm_id in EXCLUDED_PERMISSIONS[role_id]:
                continue
            # Accounts role specific filter for allowed modules and excluded permissions
            if role_id == "accounts":
                allowed_modules = {"attendance", "reimbursement", "payroll"}
                if perm.get("module") not in allowed_modules or perm_id in ACCOUNTS_EXCLUDED_PERMISSIONS:
                    continue
            
            # Determine scopes
            scopes = [base_scope]
            if role_id == "manager":
                manager_self_and_team = {
                    "attendance.read", "attendance.manage",
                    "leave.read", "leave.apply", "leave.approve",
                    "reimbursement.read", "reimbursement.create", "reimbursement.approve",
                    "employee.read", "payroll.salary.read", "payroll.pf.read", "payroll.esi.read"
                }
                if perm_id in manager_self_and_team:
                    scopes = ["SELF", "TEAM"]
                elif perm_id == "organization.read":
                    scopes = ["COMPANY"]

            now = datetime.utcnow()
            mapping_doc = {
                "roleId": role_id,
                "permissionId": perm_id,
                "scopes": scopes,
                "isActive": True,
                "version": 1,
                "effectiveFrom": None,
                "effectiveTo": None,
                "createdAt": now,
                "updatedAt": now,
                "createdBy": None,
                "updatedBy": None,
            }
            existing = await db.role_permissions.find_one({"roleId": role_id, "permissionId": perm_id})
            if not existing:
                await db.role_permissions.insert_one(mapping_doc)
                created_mappings += 1
                # History entry for ADD
                history_doc = {
                    "roleId": role_id,
                    "permissionId": perm_id,
                    "previousScopes": None,
                    "newScopes": scopes,
                    "previousState": None,
                    "newState": True,
                    "changeType": "ADD",
                    "version": 1,
                    "changedBy": None,
                    "changedAt": now,
                    "reason": "Initial seed",
                }
                await db.role_permission_history.insert_one(history_doc)
                added_history += 1
            else:
                # If scope differs, treat as UPDATE
                existing_scopes = existing.get("scopes", [])
                if existing.get("scope"):
                    existing_scopes = [existing.get("scope")]

                if set(existing_scopes) != set(scopes):
                    history_doc = {
                        "roleId": role_id,
                        "permissionId": perm_id,
                        "previousScopes": existing_scopes,
                        "newScopes": scopes,
                        "previousState": existing.get("isActive"),
                        "newState": True,
                        "changeType": "UPDATE",
                        "version": existing.get("version", 1) + 1,
                        "changedBy": None,
                        "changedAt": now,
                        "reason": "Scope change during reseed",
                    }
                    await db.role_permission_history.insert_one(history_doc)
                    added_history += 1
                    
                    update_dict = {"scopes": scopes, "updatedAt": now, "version": existing.get("version", 1) + 1}
                    if "scope" in existing:
                        update_dict["scope"] = None # Optional: remove legacy field or keep None

                    await db.role_permissions.update_one(
                        {"roleId": role_id, "permissionId": perm_id},
                        {"$set": update_dict}
                    )
                # No action needed when existing scopes match default.

    return {
        "created_roles": created_roles,
        "created_mappings": created_mappings,
        "added_history": added_history,
        "conflicts": conflicts,
    }

if __name__ == "__main__":
    import asyncio
    from app.db.mongo import get_database

    async def main():
        db = get_database()
        result = await seed_roles_and_mappings(db)
        print("Seed result:", result)
        if result["conflicts"]:
            import sys
            sys.exit(1)

    asyncio.run(main())
