import os
import re
from pymongo import MongoClient
from datetime import datetime

# Load settings via the application's config (includes .env loading)
from app.core.config import get_settings

settings = get_settings()
mongo_uri = settings.mongo_uri
mongo_db_name = settings.mongo_db_name

if not mongo_uri:
    raise RuntimeError('MONGODB_URI not configured')

# Mask credentials for reporting
masked_uri = re.sub(r'([^:/]+):([^@]+)@', r'***:***@', mongo_uri)

client = MongoClient(mongo_uri)
db = client[mongo_db_name]

# Collections to inspect
collections = ['roles', 'permissions', 'role_permissions', 'role_permission_history', 'users']

# Load canonical permissions from the seed file
import importlib.util, pathlib, sys
seed_path = pathlib.Path('backend/app/permission/engine/seed_permissions.py').resolve()
spec = importlib.util.spec_from_file_location('seed_permissions', str(seed_path))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
CANONICAL_PERMISSIONS = getattr(module, 'CANONICAL_PERMISSIONS', [])

# Helper to get field safely
def get_field(doc, field, default=None):
    return doc.get(field, default)

report_lines = []
report_lines.append('# RBAC DATABASE RECONCILIATION')
report_lines.append('')
report_lines.append(f'**Database Host**: {masked_uri}')
report_lines.append(f'**Database Name**: {mongo_db_name}')
report_lines.append(f'**Collections Inspected**: {", ".join(collections)}')
report_lines.append('')

# 2. Audit roles
roles_coll = db['roles']
all_roles = list(roles_coll.find())
role_ids = [r.get('roleId') for r in all_roles]
approved_roles = [
    'employee', 'manager', 'hr', 'admin', 'accounts', 'accounts_md', 'super_admin'
]
report_lines.append('## Roles')
report_lines.append(f'Total role documents: {len(all_roles)}')
missing_roles = [r for r in approved_roles if r not in role_ids]
unexpected_roles = [r for r in role_ids if r not in approved_roles]
duplicate_role_ids = [r for r, cnt in {rid: role_ids.count(rid) for rid in set(role_ids)}.items() if cnt > 1]
inactive_roles = [r.get('_id') for r in all_roles if not r.get('isActive', True)]
missing_fields = []
for r in all_roles:
    for f in ['roleId', 'name', 'isActive', 'createdAt', 'updatedAt', 'version']:
        if f not in r:
            missing_fields.append((r.get('_id'), f))
report_lines.append(f'Missing roles: {missing_roles or "None"}')
report_lines.append(f'Unexpected roles: {unexpected_roles or "None"}')
report_lines.append(f'Duplicate roleId values: {duplicate_role_ids or "None"}')
report_lines.append(f'Inactive roles (isActive=False): {inactive_roles or "None"}')
if missing_fields:
    report_lines.append('Roles missing required fields:')
    for _id, fld in missing_fields:
        report_lines.append(f' - {_id}: missing {fld}')
else:
    report_lines.append('All roles have required fields')
versions = [r.get('version') for r in all_roles if 'version' in r]
report_lines.append(f'Version values present: {sorted(set(versions))}')
report_lines.append('')

# 3. Audit permissions
perms_coll = db['permissions']
all_perms = list(perms_coll.find())
perm_ids = [p.get('permissionId') for p in all_perms]
canonical_ids = [p.get('permissionId') for p in CANONICAL_PERMISSIONS]
report_lines.append('## Permissions')
report_lines.append(f'Canonical permission count: {len(CANONICAL_PERMISSIONS)}')
report_lines.append(f'DB permission count: {len(all_perms)}')
missing_canonical = [pid for pid in canonical_ids if pid not in perm_ids]
unexpected_perms = [pid for pid in perm_ids if pid not in canonical_ids]
duplicate_perm_ids = [pid for pid, cnt in {pid: perm_ids.count(pid) for pid in set(perm_ids)}.items() if cnt > 1]
missing_permissionId_docs = [p.get('_id') for p in all_perms if 'permissionId' not in p]
legacy_only = [p.get('_id') for p in all_perms if 'permissionCode' in p and 'permissionId' not in p]
code_mismatch = []
for p in all_perms:
    if 'permissionCode' in p and 'permissionId' in p and p['permissionCode'] != p['permissionId']:
        code_mismatch.append(p.get('_id'))
inactive_perms = [p.get('_id') for p in all_perms if not p.get('isActive', True)]
missing_fields_perm = []
for p in all_perms:
    for f in ['permissionId','module','action','name','description']:
        if f not in p:
            missing_fields_perm.append((p.get('_id'), f))
report_lines.append(f'Missing canonical permissions: {missing_canonical or "None"}')
report_lines.append(f'Unexpected permissions: {unexpected_perms or "None"}')
report_lines.append(f'Duplicate permissionId values: {duplicate_perm_ids or "None"}')
report_lines.append(f'Documents missing permissionId: {missing_permissionId_docs or "None"}')
report_lines.append(f'Documents with only legacy permissionCode: {legacy_only or "None"}')
report_lines.append(f'Documents where permissionCode != permissionId: {code_mismatch or "None"}')
report_lines.append(f'Inactive permissions: {inactive_perms or "None"}')
if missing_fields_perm:
    report_lines.append('Permissions missing required fields:')
    for _id, fld in missing_fields_perm:
        report_lines.append(f' - {_id}: missing {fld}')
else:
    report_lines.append('All permissions have required fields')
report_lines.append('')

# 4. Audit role_permissions
rp_coll = db['role_permissions']
all_rp = list(rp_coll.find())
# Build approved matrix dict (hardcoded according to user request)
approved_matrix = {
    'employee': {
        'employee.read': 'SELF',
        'attendance.read': 'SELF',
        'leave.read': 'SELF',
        'leave.apply': 'SELF',
        'reimbursement.read': 'SELF',
        'reimbursement.create': 'SELF',
        'payroll.read': 'SELF',
        'payroll.salary.read': 'SELF',
    },
    'manager': {
        'employee.read': 'TEAM',
        'attendance.read': 'TEAM',
        'leave.read': 'TEAM',
        'leave.approve': 'TEAM',
        'reimbursement.read': 'TEAM',
        'reimbursement.approve': 'TEAM',
    },
    'hr': {
        'employee.read': 'GLOBAL',
        'employee.manage': 'GLOBAL',
        'attendance.read': 'GLOBAL',
        'attendance.manage': 'GLOBAL',
        'attendance.sync': 'GLOBAL',
        'leave.read': 'GLOBAL',
        'leave.manage': 'GLOBAL',
        'reimbursement.read': 'GLOBAL',
        'reimbursement.manage': 'GLOBAL',
        'organization.read': 'GLOBAL',
    },
    'admin': {
        'employee.read': 'GLOBAL',
        'employee.manage': 'GLOBAL',
        'attendance.read': 'GLOBAL',
        'attendance.manage': 'GLOBAL',
        'attendance.sync': 'GLOBAL',
        'leave.read': 'GLOBAL',
        'leave.manage': 'GLOBAL',
        'reimbursement.read': 'GLOBAL',
        'reimbursement.manage': 'GLOBAL',
        'payroll.read': 'GLOBAL',
        'payroll.salary.read': 'GLOBAL',
        'payroll.calculate': 'GLOBAL',
        'payroll.publish': 'GLOBAL',
        'payroll.cycle.read': 'GLOBAL',
        'payroll.cycle.manage': 'GLOBAL',
        'organization.read': 'GLOBAL',
        'organization.manage': 'GLOBAL',
    },
    'accounts': {
        'attendance.read': 'COMPANY',
        'reimbursement.read': 'COMPANY',
        'payroll.read': 'COMPANY',
        'payroll.pf.read': 'COMPANY',
        'payroll.esi.read': 'COMPANY',
        'payroll.branch_summary.read': 'COMPANY',
        'payroll.cycle.read': 'COMPANY',
    },
    'accounts_md': {
        'employee.read': 'GLOBAL',
        'attendance.read': 'GLOBAL',
        'reimbursement.read': 'GLOBAL',
        'payroll.read': 'GLOBAL',
        'payroll.salary.read': 'GLOBAL',
        'payroll.pf.read': 'GLOBAL',
        'payroll.esi.read': 'GLOBAL',
        'payroll.branch_summary.read': 'GLOBAL',
        'payroll.calculate': 'GLOBAL',
        'payroll.publish': 'GLOBAL',
        'payroll.cycle.read': 'GLOBAL',
        'payroll.cycle.manage': 'GLOBAL',
    },
    'super_admin': {pid: 'GLOBAL' for pid in canonical_ids},
}
# Expand policy.*.manage entries for hr and admin
policy_manage_perms = [p['permissionId'] for p in CANONICAL_PERMISSIONS if p['permissionId'].startswith('policy.') and p['permissionId'].endswith('.manage')]
for role in ('hr', 'admin'):
    for pid in policy_manage_perms:
        approved_matrix[role][pid] = 'GLOBAL'

expected_entries = []
for role, perms in approved_matrix.items():
    for perm_id, scope in perms.items():
        expected_entries.append((role, perm_id, scope))

# Analyze mappings
missing_mappings = []
extra_mappings = []
incorrect_scope = []
inactive_mappings = []
legacy_code_mismatches = []
for role, perm_id, expected_scope in expected_entries:
    docs = [d for d in all_rp if d.get('roleId') == role and d.get('permissionId') == perm_id]
    if not docs:
        missing_mappings.append((role, perm_id, expected_scope))
    else:
        for d in docs:
            if d.get('scope') != expected_scope:
                incorrect_scope.append((role, perm_id, expected_scope, d.get('scope')))
            if not d.get('isActive', True):
                inactive_mappings.append((role, perm_id))
            if 'permissionCode' in d and d.get('permissionCode') != perm_id:
                legacy_code_mismatches.append((d.get('_id'), d.get('permissionCode')))
# Extra mappings not in approved matrix
approved_set = {(r, p) for r, p, _ in expected_entries}
for d in all_rp:
    key = (d.get('roleId'), d.get('permissionId'))
    if key not in approved_set:
        extra_mappings.append(key)
# Duplicate (roleId, permissionId, scope)
seen = set()
duplicate_role_perm_scope = []
for d in all_rp:
    key = (d.get('roleId'), d.get('permissionId'), d.get('scope'))
    if key in seen:
        duplicate_role_perm_scope.append(key)
    else:
        seen.add(key)

report_lines.append('## Role Permissions')
report_lines.append(f'Total role_permission documents: {len(all_rp)}')
report_lines.append(f'Missing mappings (should exist): {len(missing_mappings)}')
if missing_mappings:
    for r, p, s in missing_mappings[:10]:
        report_lines.append(f' - Missing: role={r}, permission={p}, expectedScope={s}')
report_lines.append(f'Extra mappings (should not exist): {len(extra_mappings)}')
if extra_mappings:
    for r, p in extra_mappings[:10]:
        report_lines.append(f' - Extra: role={r}, permission={p}')
report_lines.append(f'Incorrect scopes: {len(incorrect_scope)}')
if incorrect_scope:
    for r, p, exp, act in incorrect_scope[:10]:
        report_lines.append(f' - Scope mismatch: role={r}, perm={p}, expected={exp}, actual={act}')
report_lines.append(f'Inactive mappings: {len(inactive_mappings)}')
if inactive_mappings:
    for r, p in inactive_mappings[:10]:
        report_lines.append(f' - Inactive: role={r}, permission={p}')
report_lines.append(f'Legacy permissionCode mismatches: {len(legacy_code_mismatches)}')
if legacy_code_mismatches:
    for _id, code in legacy_code_mismatches[:10]:
        report_lines.append(f' - Legacy code: _id={_id}, code={code}')
report_lines.append(f'Duplicate (roleId, permissionId, scope) entries: {len(duplicate_role_perm_scope)}')
if duplicate_role_perm_scope:
    for dup in duplicate_role_perm_scope[:10]:
        report_lines.append(f' - Duplicate: {dup}')
report_lines.append('')

# 5. Matrix differences summary
report_lines.append('## Matrix Differences Summary')
report_lines.append(f'Missing mappings: {len(missing_mappings)}')
report_lines.append(f'Extra mappings: {len(extra_mappings)}')
report_lines.append(f'Wrong scopes: {len(incorrect_scope)}')
report_lines.append('')

# 6. Role permission history audit
history_coll = db['role_permission_history']
all_hist = list(history_coll.find())
report_lines.append('## Role Permission History')
report_lines.append(f'Total history records: {len(all_hist)}')
combos = set((h.get('roleId'), h.get('permissionId')) for h in all_hist)
report_lines.append(f'Unique role/permission combinations in history: {len(combos)}')
# Missing ADD history for current mappings
missing_history = []
for doc in all_rp:
    if not any(h.get('roleId') == doc.get('roleId') and h.get('permissionId') == doc.get('permissionId') and h.get('changeType') == 'ADD' for h in all_hist):
        missing_history.append((doc.get('roleId'), doc.get('permissionId')))
report_lines.append(f'Mappings missing ADD history: {len(missing_history)}')
# Duplicate versions per combo
duplicate_versions = []
for combo in combos:
    versions = [h.get('version') for h in all_hist if h.get('roleId') == combo[0] and h.get('permissionId') == combo[1]]
    if len(versions) != len(set(versions)):
        duplicate_versions.append(combo)
report_lines.append(f'Combination with duplicate version numbers: {len(duplicate_versions)}')
# Invalid changeType
invalid_change = [h.get('_id') for h in all_hist if h.get('changeType') not in ('ADD', 'UPDATE', 'REMOVE')]
report_lines.append(f'History records with invalid changeType: {len(invalid_change)}')
# Version gaps
version_gaps = []
for combo in combos:
    vers = sorted([h.get('version') for h in all_hist if h.get('roleId') == combo[0] and h.get('permissionId') == combo[1]])
    if vers:
        expected = list(range(1, vers[-1] + 1))
        if vers != expected:
            version_gaps.append((combo, vers))
report_lines.append(f'History version gaps: {len(version_gaps)}')
report_lines.append('')

# 7. Users audit
users_coll = db['users']
all_users = list(users_coll.find())
report_lines.append('## Users')
report_lines.append(f'Total users: {len(all_users)}')
users_with_role = [u for u in all_users if u.get('roleId')]
users_without_role = [u for u in all_users if not u.get('roleId')]
report_lines.append(f'Users with roleId: {len(users_with_role)}')
report_lines.append(f'Users without roleId: {len(users_without_role)}')
role_ids_set = set(role_ids)
invalid_role_refs = [u.get('_id') for u in users_with_role if u.get('roleId') not in role_ids_set]
report_lines.append(f'Users whose roleId does not exist in roles collection: {len(invalid_role_refs)}')
legacy_conflicts = []
for u in all_users:
    if 'roleCode' in u and u.get('roleCode') != u.get('roleId'):
        legacy_conflicts.append(u.get('_id'))
report_lines.append(f'Users with legacy role conflicts: {len(legacy_conflicts)}')
users_no_company = [u.get('_id') for u in all_users if not u.get('companyId')]
report_lines.append(f'Users without companyId: {len(users_no_company)}')
users_no_branch = [u.get('_id') for u in all_users if not u.get('branchId')]
report_lines.append(f'Users without branchId: {len(users_no_branch)}')
# authorizationVersion distribution
auth_versions = {}
for u in all_users:
    v = u.get('authorizationVersion')
    auth_versions[v] = auth_versions.get(v, 0) + 1
report_lines.append('AuthorizationVersion distribution:')
for v, cnt in auth_versions.items():
    report_lines.append(f' - {v}: {cnt}')
report_lines.append('')

# 8. Super Admin 5188 inspection
emp_id = 5188
user_5188 = users_coll.find_one({'empId': emp_id})
report_lines.append('## Super Admin 5188')
if user_5188:
    report_lines.append(f"User _id: {user_5188.get('_id')}")
    report_lines.append(f"roleId: {user_5188.get('roleId')}")
    report_lines.append(f"authorizationVersion: {user_5188.get('authorizationVersion')}")
    report_lines.append(f"companyId: {user_5188.get('companyId')}")
    report_lines.append(f"branchId: {user_5188.get('branchId')}")
    role_doc = roles_coll.find_one({'roleId': user_5188.get('roleId')})
    resolved = role_doc.get('roleId') if role_doc else None
    report_lines.append(f"Resolved roleId in roles collection: {resolved}")
    if resolved == 'super_admin':
        missing_perm = []
        for perm in CANONICAL_PERMISSIONS:
            pid = perm.get('permissionId')
            mapping = rp_coll.find_one({'roleId': 'super_admin', 'permissionId': pid})
            if not mapping or mapping.get('scope') != 'GLOBAL':
                missing_perm.append(pid)
        report_lines.append(f"Missing or incorrect GLOBAL permissions for Super Admin: {len(missing_perm)}")
        if missing_perm:
            report_lines.append(' - ' + ', '.join(missing_perm[:10]))
    else:
        report_lines.append('User 5188 does not have Super Admin role')
else:
    report_lines.append('User with empId 5188 not found')
report_lines.append('')

# 9. Index audit
report_lines.append('## Index Status')
for coll_name in collections:
    coll = db[coll_name]
    indexes = list(coll.list_indexes())
    report_lines.append(f'Collection `{coll_name}` indexes:')
    for idx in indexes:
        keys = idx.get('key')
        uniq = idx.get('unique', False)
        report_lines.append(f' - {dict(keys)} (unique={uniq})')
report_lines.append('')

# Final statement
report_lines.append('WRITE OPERATIONS EXECUTED: 0')

print('\n'.join(report_lines))
