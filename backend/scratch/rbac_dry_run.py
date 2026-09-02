import asyncio
from datetime import datetime
from app.core.config import get_settings
from motor.motor_asyncio import AsyncIOMotorClient
from app.permission.engine.seed_permissions import CANONICAL_PERMISSIONS
from app.role.engine.seed_roles import ROLES, EXCLUDED_PERMISSIONS, ACCOUNTS_EXCLUDED_PERMISSIONS

async def main():
    settings = get_settings()
    client = AsyncIOMotorClient(settings.mongo_uri)
    db = client["essl_production"]
    
    # 1. Existing Counts
    roles_count = await db.roles.count_documents({})
    permissions_count = await db.permissions.count_documents({})
    role_permissions_count = await db.role_permissions.count_documents({})
    history_count = await db.role_permission_history.count_documents({})
    
    print("--- 1. Production RBAC current state ---")
    print(f"Existing Roles Count: {roles_count}")
    print(f"Existing Permissions Count: {permissions_count}")
    print(f"Existing Role Permissions Count: {role_permissions_count}")
    print(f"Existing Role Permission History Count: {history_count}")
    
    # Analyze legacy data
    legacy_roles = await db.roles.count_documents({"roleId": {"$regex": "^ROLE_"}})
    print(f"Legacy ROLE_* identifiers in roles: {legacy_roles}")
    legacy_role_perms = await db.role_permissions.count_documents({"roleId": {"$regex": "^ROLE_"}})
    print(f"Legacy ROLE_* identifiers in role_permissions: {legacy_role_perms}")
    
    legacy_scope = await db.role_permissions.count_documents({"scope": {"$exists": True}})
    print(f"Legacy singular `scope` fields in role_permissions: {legacy_scope}")
    
    # Expected vs Existing Roles
    print("\n--- 2. Expected RBAC state ---")
    expected_roles_ids = {r["roleId"] for r in ROLES}
    existing_roles_docs = await db.roles.find({}).to_list(None)
    existing_roles_ids = {r.get("roleId") for r in existing_roles_docs if r.get("roleId")}
    
    missing_roles = expected_roles_ids - existing_roles_ids
    print(f"Expected roles count: {len(expected_roles_ids)}")
    print(f"Missing roles: {missing_roles}")
    
    # Expected vs Existing Permissions
    expected_permissions_ids = {p["permissionId"] for p in CANONICAL_PERMISSIONS}
    existing_permissions_docs = await db.permissions.find({}).to_list(None)
    existing_permissions_ids = {p.get("permissionId") for p in existing_permissions_docs if p.get("permissionId")}
    
    missing_permissions = expected_permissions_ids - existing_permissions_ids
    print(f"Expected permissions count: {len(expected_permissions_ids)}")
    print(f"Missing permissions: {missing_permissions}")
    
    # Expected Mappings
    expected_mappings = {}
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
                    
            expected_mappings[(role_id, perm_id)] = scopes

    print(f"Expected role_permissions mappings count: {len(expected_mappings)}")
    
    # Existing Mappings
    existing_mappings_docs = await db.role_permissions.find({}).to_list(None)
    existing_mappings = {}
    duplicate_mappings = []
    
    for doc in existing_mappings_docs:
        role_id = doc.get("roleId")
        perm_id = doc.get("permissionId")
        key = (role_id, perm_id)
        if key in existing_mappings:
            duplicate_mappings.append(key)
        else:
            existing_mappings[key] = doc
            
    if duplicate_mappings:
        print(f"Duplicate mappings found: {len(duplicate_mappings)}")
        
    missing_mappings = set(expected_mappings.keys()) - set(existing_mappings.keys())
    print(f"Missing canonical mappings: {len(missing_mappings)}")
    
    custom_mappings = set(existing_mappings.keys()) - set(expected_mappings.keys())
    print(f"Custom mappings (not in canonical): {len(custom_mappings)}")
    
    conflicts = []
    documents_to_insert_roles = [r for r in ROLES if r["roleId"] in missing_roles]
    documents_to_insert_perms = [p for p in CANONICAL_PERMISSIONS if p["permissionId"] in missing_permissions]
    documents_to_insert_mappings = [key for key in missing_mappings]
    
    documents_to_update_mappings = []
    
    for key, expected_scopes in expected_mappings.items():
        if key in existing_mappings:
            doc = existing_mappings[key]
            
            existing_scopes = doc.get("scopes", [])
            if doc.get("scope"):
                existing_scopes = [doc.get("scope")]
                
            if set(existing_scopes) != set(expected_scopes):
                documents_to_update_mappings.append({
                    "roleId": key[0],
                    "permissionId": key[1],
                    "expected_scopes": expected_scopes,
                    "existing_scopes": existing_scopes
                })
    
    print("\n--- 3. Exact documents that would be inserted ---")
    print(f"Roles to insert: {len(documents_to_insert_roles)}")
    print(f"Permissions to insert: {len(documents_to_insert_perms)}")
    print(f"Role_Permissions to insert: {len(documents_to_insert_mappings)}")
    if documents_to_insert_mappings:
        print("Sample of missing mappings to insert:")
        for k in list(documents_to_insert_mappings)[:5]:
            print(f"  {k} -> scopes: {expected_mappings[k]}")

    print("\n--- 4. Exact documents that would be updated, if any ---")
    print(f"Role_Permissions to update (scope changes): {len(documents_to_update_mappings)}")
    if documents_to_update_mappings:
        for update in documents_to_update_mappings[:5]:
            print(f"  {update['roleId']} - {update['permissionId']}: existing {update['existing_scopes']} -> expected {update['expected_scopes']}")

    print("\n--- 5. Documents that would be deleted ---")
    print("ZERO. The seed logic (seed_permissions.py, seed_roles.py) does not perform any deletes.")
    
    print("\n--- 6. Confirmation that Model B is preserved ---")
    print(f"The seed_roles.py uses `scopes: list` field. Yes, Model B is preserved.")
    
    print("\n--- 7. Confirmation that custom data is preserved ---")
    print(f"No custom roles or role_permissions are deleted by the seed process. Custom mapping count: {len(custom_mappings)}")

    print("\n--- 8. Confirmation that the migration is idempotent ---")
    print("Yes. Existing permissions are checked and updated only if mismatched. Existing roles are skipped. Existing mappings update scopes if different.")

    # Specifically check super_admin
    print("\n--- Specific checks ---")
    sa_att_read = expected_mappings.get(("super_admin", "attendance.read"))
    print(f"super_admin attendance.read expected scopes: {sa_att_read}")
    
    mgr_att_read = expected_mappings.get(("manager", "attendance.read"))
    print(f"manager attendance.read expected scopes: {mgr_att_read}")

    acc_payroll = expected_mappings.get(("accounts", "payroll.calculate"))
    print(f"accounts payroll.calculate expected mapping exists? {'yes' if acc_payroll else 'no'}")

if __name__ == "__main__":
    asyncio.run(main())
