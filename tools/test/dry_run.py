import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import sys
from datetime import datetime

# Import definitions to avoid duplicating them
import sys
import os
sys.path.append(os.path.abspath('c:/ess/ess_sample_2/backend'))

from app.permission.engine.seed_permissions import CANONICAL_PERMISSIONS
from app.role.engine.seed_roles import ROLES, EXCLUDED_PERMISSIONS, ACCOUNTS_EXCLUDED_PERMISSIONS

async def dry_run():
    try:
        client = AsyncIOMotorClient('mongodb+srv://lokeshca2004_db_user:maYiWdAooh5Qw7QM@cluster0.aehbv6j.mongodb.net/')
        db = client['essl_production']
        
        roles_count = await db.roles.count_documents({})
        perms_count = await db.permissions.count_documents({})
        mappings_count = await db.role_permissions.count_documents({})
        history_count = await db.role_permission_history.count_documents({})
        
        print(f"--- CURRENT STATE ---")
        print(f"roles count: {roles_count}")
        print(f"permissions count: {perms_count}")
        print(f"role_permissions count: {mappings_count}")
        print(f"role_permission_history count: {history_count}")
        
        print("\n--- EXPECTED ROLES ---")
        for r in ROLES:
            print(f"- {r['roleId']}")
            
        print("\n--- EXPECTED PERMISSIONS (Total: {}) ---".format(len(CANONICAL_PERMISSIONS)))
        
        print("\n--- EXPECTED ROLE_PERMISSIONS SUMMARY ---")
        expected_mappings = []
        for role in ROLES:
            role_id = role["roleId"]
            base_scope = role["scope"]
            for perm in CANONICAL_PERMISSIONS:
                perm_id = perm["permissionId"]
                
                if role_id in EXCLUDED_PERMISSIONS and perm_id in EXCLUDED_PERMISSIONS[role_id]:
                    continue
                if role_id == "accounts":
                    allowed_modules = {"attendance", "reimbursement", "payroll"}
                    if perm.get("module") not in allowed_modules or perm_id in ACCOUNTS_EXCLUDED_PERMISSIONS:
                        continue
                        
                scopes = [base_scope]
                if role_id == "manager":
                    manager_self_and_team = {
                        "attendance.read", "attendance.manage", "attendance.sync",
                        "leave.read", "leave.apply", "leave.approve",
                        "reimbursement.read", "reimbursement.create", "reimbursement.approve",
                        "employee.read", "payroll.salary.read", "payroll.pf.read", "payroll.esi.read"
                    }
                    if perm_id in manager_self_and_team:
                        scopes = ["SELF", "TEAM"]
                        
                expected_mappings.append({"roleId": role_id, "permissionId": perm_id, "scopes": scopes})
                
        print(f"Total expected mappings: {len(expected_mappings)}")
        
        print("\n--- MISSING DOCUMENTS ---")
        missing_roles = []
        for r in ROLES:
            if not await db.roles.find_one({"roleId": r["roleId"]}):
                missing_roles.append(r["roleId"])
        print(f"Missing roles: {missing_roles}")
        
        missing_perms = []
        for p in CANONICAL_PERMISSIONS:
            if not await db.permissions.find_one({"permissionId": p["permissionId"]}):
                missing_perms.append(p["permissionId"])
        print(f"Missing permissions: {len(missing_perms)} (all missing? {len(missing_perms) == len(CANONICAL_PERMISSIONS)})")
        
        missing_mappings = 0
        conflicting_mappings = 0
        incorrect_scopes = 0
        legacy_singular_scope = 0
        duplicates = 0
        
        for em in expected_mappings:
            existing = await db.role_permissions.find({"roleId": em["roleId"], "permissionId": em["permissionId"]}).to_list(None)
            if len(existing) == 0:
                missing_mappings += 1
            elif len(existing) > 1:
                duplicates += 1
            else:
                doc = existing[0]
                if "scope" in doc:
                    legacy_singular_scope += 1
                if set(doc.get("scopes", [])) != set(em["scopes"]):
                    incorrect_scopes += 1
                    conflicting_mappings += 1
                    
        print(f"Missing role mappings: {missing_mappings}")
        print(f"Conflicting mappings: {conflicting_mappings}")
        print(f"Legacy singular scope fields detected: {legacy_singular_scope}")
        print(f"Duplicate mappings: {duplicates}")
        print(f"Incorrect scopes: {incorrect_scopes}")
        
        print("\n--- SPECIFIC CHECK: Super Admin attendance.read ---")
        for em in expected_mappings:
            if em["roleId"] == "super_admin" and em["permissionId"] == "attendance.read":
                print(f"Expected: {em}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(dry_run())
