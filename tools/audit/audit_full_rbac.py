import asyncio
import json
from app.db.mongo import get_database
from backend.app.permission.engine.seed_permissions import CANONICAL_PERMISSIONS

async def audit():
    db = get_database()
    # Permissions collection
    perms = await db.permissions.find().to_list(length=None)
    total_perms = len(perms)
    missing_permId = [p for p in perms if not p.get('permissionId')]
    with_permCode = [p for p in perms if p.get('permissionCode')]
    # Role permissions collection
    role_perms = await db.role_permissions.find().to_list(length=None)
    total_role_perms = len(role_perms)
    missing_rp_permId = [rp for rp in role_perms if not rp.get('permissionId')]
    with_rp_permCode = [rp for rp in role_perms if rp.get('permissionCode')]
    # Role permission history count
    rp_history_count = await db.role_permission_history.count_documents({})
    # Canonical IDs set
    canonical_ids = {p['permissionId'] for p in CANONICAL_PERMISSIONS}
    # Determine missing canonical permissions in DB
    db_perm_ids = {p.get('permissionId') for p in perms if p.get('permissionId')}
    missing_canonical = canonical_ids - db_perm_ids
    # Verify each role_permission references a valid permissionId (after migration it will be permissionCode if missing)
    invalid_refs = []
    for rp in role_perms:
        pid = rp.get('permissionId') or rp.get('permissionCode')
        if pid and pid not in canonical_ids:
            invalid_refs.append(rp)
    # Build report
    report = {
        'total_permissions': total_perms,
        'permissions_missing_permissionId_count': len(missing_permId),
        'permissions_with_permissionCode_count': len(with_permCode),
        'permissions_documents': [
            {
                '_id': p['_id'],
                'permissionCode': p.get('permissionCode'),
                'permissionId': p.get('permissionId'),
                'module': p.get('module'),
                'action': p.get('action')
            } for p in perms
        ],
        'missing_canonical_permissions': list(missing_canonical),
        'total_role_permissions': total_role_perms,
        'role_permissions_missing_permissionId_count': len(missing_rp_permId),
        'role_permissions_with_permissionCode_count': len(with_rp_permCode),
        'role_permissions_documents': [
            {
                '_id': rp['_id'],
                'roleId': rp.get('roleId'),
                'permissionCode': rp.get('permissionCode'),
                'permissionId': rp.get('permissionId'),
                'scope': rp.get('scope')
            } for rp in role_perms
        ],
        'role_permissions_invalid_refs': invalid_refs,
        'role_permission_history_count': rp_history_count,
        'canonical_permission_ids': list(canonical_ids)
    }
    print(json.dumps(report, indent=2, default=str))

if __name__ == '__main__':
    asyncio.run(audit())
