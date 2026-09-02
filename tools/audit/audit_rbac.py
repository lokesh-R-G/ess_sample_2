import asyncio
import json
from app.db.mongo import get_database
from backend.app.permission.engine.seed_permissions import CANONICAL_PERMISSIONS

async def audit():
    db = get_database()
    # Permissions collection
    perms_cursor = db.permissions.find()
    perms = await perms_cursor.to_list(length=None)
    total_perms = await db.permissions.count_documents({})
    missing_or_null = [p for p in perms if not p.get('permissionId')]
    # Find duplicate non-null permissionId values
    perm_ids = [p['permissionId'] for p in perms if p.get('permissionId')]
    dup_ids = {pid for pid in perm_ids if perm_ids.count(pid) > 1}
    dup_records = [p for p in perms if p.get('permissionId') in dup_ids]
    # Compare with canonical catalog
    canonical_ids = {p['permissionId'] for p in CANONICAL_PERMISSIONS}
    legacy = [p for p in perms if p.get('permissionId') and p['permissionId'] not in canonical_ids]
    # Role permissions
    rp_cursor = db.role_permissions.find()
    role_perms = await rp_cursor.to_list(length=None)
    rp_missing = [rp for rp in role_perms if not rp.get('permissionId')]
    rp_invalid_refs = [rp for rp in role_perms if rp.get('permissionId') and rp['permissionId'] not in canonical_ids]
    # Summarize
    report = {
        'total_permissions': total_perms,
        'missing_or_null_permissionId': missing_or_null,
        'duplicate_permissionId_records': dup_records,
        'legacy_permission_records': legacy,
        'role_permissions_count': len(role_perms),
        'role_permissions_missing_permissionId': rp_missing,
        'role_permissions_invalid_refs': rp_invalid_refs,
        'canonical_permission_ids': list(canonical_ids)
    }
    print(json.dumps(report, default=str, indent=2))

if __name__ == '__main__':
    asyncio.run(audit())
