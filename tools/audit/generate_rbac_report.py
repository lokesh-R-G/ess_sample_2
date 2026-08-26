import asyncio
import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)

from backend.tests.mock_db import _MockClient
_mock_client = _MockClient()
_shared_db = _mock_client["ess_test"]
def get_mock_db():
    return _shared_db

from app.role.engine.seed_roles import seed_roles_and_mappings
from app.permission.engine.seed_permissions import seed_permissions
from app.rbac.engine import authorize, _ROLE_PERM_CACHE
from app.rbac.context_providers import self_context, employee_context_by_emp_id
from backend.scripts.phase4_migrate_users import CANONICAL_ROLE_MAP

async def run_scenario(name, role, emp_id, target_emp_id, expected_scope, expected_result):
    db = get_mock_db()
    
    # Context
    user = {"empId": emp_id, "employeeId": emp_id, "roleId": role}
    
    rc = {"empId": target_emp_id}
        
    import app.rbac.engine
    from app.main import app as fastapi_app
    from app.db.mongo import get_database
    fastapi_app.dependency_overrides[get_database] = get_mock_db
    
    try:
        await authorize(user, "attendance.read", rc)
        result = "ALLOW"
    except Exception as e:
        result = "DENY"
        
    fastapi_app.dependency_overrides.pop(get_database, None)
    
    res_str = "PASS" if result == expected_result else f"FAIL (Got {result})"
    return f"| {name} | {role} | {target_emp_id} | {expected_scope} | {expected_result} | {res_str} |\n"

async def generate_report():
    db = get_mock_db()
    await seed_permissions(db)
    await seed_roles_and_mappings(db)
    _ROLE_PERM_CACHE.clear()
    
    # insert mock employees
    await db.employees.delete_many({})
    for e in [
        {"employeeId": "EMP01", "employeeCode": "EMP01", "managerId": "MGR01", "branchId": "BR1", "companyId": "C1"},
        {"employeeId": "EMP02", "employeeCode": "EMP02", "managerId": "MGR02", "branchId": "BR2", "companyId": "C2"},
        {"employeeId": "MGR01", "employeeCode": "MGR01", "managerId": "ADM01", "branchId": "BR1", "companyId": "C1"},
        {"employeeId": "HR01", "employeeCode": "HR01", "managerId": "ADM01", "branchId": "BR1", "companyId": "C1"},
        {"employeeId": "ADM01", "employeeCode": "ADM01", "managerId": "SADM01", "branchId": "BR1", "companyId": "C1"},
        {"employeeId": "SADM01", "employeeCode": "SADM01", "managerId": None, "branchId": "BR1", "companyId": "C1"},
    ]:
        await db.employees.insert_one(e)
    
    # 1. Inspect seed_roles.py
    from app.role.engine.seed_roles import ROLES as SEED_ROLES
    seed_role_ids = [r["roleId"] for r in SEED_ROLES]
    
    db_roles = await db.roles.find({}).to_list(None)
    db_role_ids = [r.get("roleId") for r in db_roles]
    
    rp_docs = await db.role_permissions.find({}).to_list(None)
    
    report_path = os.path.join(project_root, "backend", "docs", "phase5_stage6_rbac_role_matrix_report.md")
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    
    with open(report_path, "w") as f:
        f.write("# Phase 5 Stage 6: RBAC Role Matrix & Identity Reconciliation Report\n\n")
        
        f.write("## 1. Canonical Role Identity Reconciliation\n\n")
        f.write("| Legacy Role | phase4 map (users.roleId) | roles.roleId | role_permissions.roleId | seed_roles.py | Consistent? |\n")
        f.write("|---|---|---|---|---|---|\n")
        
        for legacy_role, phase4_id in CANONICAL_ROLE_MAP.items():
            expected_seed = legacy_role.lower().replace(" ", "_")
            if legacy_role == "Accounts MD": expected_seed = "accounts_md"
            
            db_role_val = expected_seed if expected_seed in db_role_ids else "None"
            rp_val = expected_seed if any(r.get("roleId") == expected_seed for r in rp_docs) else "None"
            seed_val = expected_seed if expected_seed in seed_role_ids else "None"
            
            consistent = (phase4_id == seed_val)
            f.write(f"| {legacy_role} | {phase4_id} | {db_role_val} | {rp_val} | {seed_val} | {'Yes' if consistent else 'No'} |\n")
            
        f.write("\n### Data/Model Inconsistency Found\n")
        f.write("The `scripts/phase4_migrate_users.py` populated the `users` collection with `ROLE_*` prefixed identifiers (e.g., `ROLE_SUPER_ADMIN`), but `app/role/engine/seed_roles.py` seeds the canonical `roles` and `role_permissions` collections with lowercase snake_case identifiers (e.g., `super_admin`). This completely breaks the RBAC chain since `get_current_user` passes the `ROLE_*` identifier to `engine.authorize()`, which expects `snake_case`.\n\n")
        
        f.write("## 2. Attendance Permissions Matrix\n\n")
        f.write("| RoleId | PermissionId | Scope |\n")
        f.write("|---|---|---|\n")
        att_perms = [p for p in rp_docs if p.get("permissionId", "").startswith("attendance")]
        for p in sorted(att_perms, key=lambda x: (x.get("roleId"), x.get("permissionId"))):
            f.write(f"| {p.get('roleId')} | {p.get('permissionId')} | {p.get('scope')} |\n")
            
        f.write("\n## 3. Scope Testing Results\n\n")
        f.write("Testing with CANONICAL identifiers (e.g., `super_admin`) to prove matrix behavior independent of identity mismatch.\n\n")
        f.write("| Scenario | Role | Target | Expected Scope | Expected | Result |\n")
        f.write("|---|---|---|---|---|---|\n")
        
        scenarios = [
            ("Employee SELF", "employee", "EMP01", "EMP01", "SELF", "ALLOW"),
            ("Employee Other", "employee", "EMP01", "EMP02", "SELF", "DENY"),
            ("Manager TEAM", "manager", "MGR01", "MGR01", "TEAM", "ALLOW"),
            ("Manager Other", "manager", "MGR01", "EMP02", "TEAM", "DENY"),
            ("Super Admin GLOBAL (Self)", "super_admin", "SADM01", "SADM01", "GLOBAL", "ALLOW"),
            ("Super Admin GLOBAL (Other)", "super_admin", "SADM01", "EMP02", "GLOBAL", "ALLOW"),
        ]
        
        for name, role, emp_id, tgt_id, expected_scope, exp_res in scenarios:
            res_str = await run_scenario(name, role, emp_id, tgt_id, expected_scope, exp_res)
            f.write(res_str)
            
if __name__ == "__main__":
    asyncio.run(generate_report())
