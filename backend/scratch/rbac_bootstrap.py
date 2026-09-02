import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import get_settings
from app.permission.engine.seed_permissions import seed_permissions
from app.role.engine.seed_roles import seed_roles_and_mappings

async def main():
    settings = get_settings()
    
    print("--- 1. PRE-WRITE ASSERTION ---")
    print(f"Configured Database URI: {settings.mongo_uri}")
    print(f"Configured Database Name: {settings.mongo_db_name}")
    
    if settings.mongo_db_name != "essl_production":
        print("ERROR: Database is not essl_production")
        return
        
    client = AsyncIOMotorClient(settings.mongo_uri)
    db = client[settings.mongo_db_name]
    
    existing_roles = await db.roles.find({}).to_list(None)
    print(f"Existing Roles Count: {len(existing_roles)}")
    for r in existing_roles:
        print(f"Existing Role: {r.get('roleId')} | Name: {r.get('name')}")
        
    print("\n--- 2. EXECUTING SEEDERS ---")
    perm_result = await seed_permissions(db)
    print(f"Permissions Seed Result: {perm_result}")
    
    roles_result = await seed_roles_and_mappings(db)
    print(f"Roles & Mappings Seed Result: {roles_result}")
    
    print("\n--- 3. READ-BACK VERIFICATION ---")
    roles_count = await db.roles.count_documents({})
    permissions_count = await db.permissions.count_documents({})
    rp_count = await db.role_permissions.count_documents({})
    history_count = await db.role_permission_history.count_documents({})
    
    print(f"Total Roles: {roles_count}")
    print(f"Total Permissions: {permissions_count}")
    print(f"Total Role Permissions: {rp_count}")
    print(f"Total History Entries: {history_count}")
    
    sa_att = await db.role_permissions.find_one({"roleId": "super_admin", "permissionId": "attendance.read"})
    print(f"super_admin + attendance.read -> {sa_att.get('scopes') if sa_att else None}")
    
    mgr_att = await db.role_permissions.find_one({"roleId": "manager", "permissionId": "attendance.read"})
    print(f"manager + attendance.read -> {mgr_att.get('scopes') if mgr_att else None}")
    
    acc_att = await db.role_permissions.find_one({"roleId": "accounts", "permissionId": "attendance.read"})
    print(f"accounts + attendance.read -> {acc_att.get('scopes') if acc_att else None}")
    
    legacy_roles = await db.roles.count_documents({"roleId": {"$regex": "^ROLE_"}})
    print(f"Legacy ROLE_* identifiers: {legacy_roles}")
    
    legacy_scope = await db.role_permissions.count_documents({"scope": {"$exists": True}})
    print(f"Legacy singular scope fields: {legacy_scope}")
    
if __name__ == "__main__":
    asyncio.run(main())
