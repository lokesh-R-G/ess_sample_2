import asyncio
import pytest
from datetime import datetime

# Import seed functions
from app.permission.engine.seed_permissions import seed_permissions, CANONICAL_PERMISSIONS
from app.role.engine.seed_roles import seed_roles_and_mappings

# Reuse the in‑memory mock database fixture from phase‑1 tests
@pytest.fixture(scope="module")
async def setup_db():
    # Load the mock DB implementation used in other tests
    from backend.tests.mock_db import _MockClient, _MockDatabase
    client = _MockClient()
    db = client["ess_test"]
    # Ensure clean collections
    await db.roles.delete_many({})
    await db.permissions.delete_many({})
    await db.role_permissions.delete_many({})
    await db.role_permission_history.delete_many({})
    # Seed data
    await seed_permissions(db)
    await seed_roles_and_mappings(db)
    yield db
    # Cleanup after test suite
    await db.roles.delete_many({})
    await db.permissions.delete_many({})
    await db.role_permissions.delete_many({})
    await db.role_permission_history.delete_many({})

# Approved default scopes per role
DEFAULT_SCOPES = {
    "employee": "SELF",
    "manager": "TEAM",
    "hr": "GLOBAL",
    "admin": "GLOBAL",
    "accounts": "COMPANY",
    "accounts_md": "GLOBAL",
    "super_admin": "GLOBAL",
}

# Permissions that Accounts must NOT receive (explicit dash entries)
EXCLUDED_FOR_ACCOUNTS = {
    "payroll.calculate",
    "payroll.publish",
    "payroll.cycle.manage",
}

# Modules that Accounts is allowed to have permissions from
ACCOUNTS_ALLOWED_MODULES = {"attendance", "reimbursement", "payroll"}

@pytest.mark.asyncio
async def test_role_permission_matrix(setup_db):
    db = setup_db

    # Verify role count
    roles = await db.roles.find({}).to_list(length=None)
    assert len(roles) == 7, f"Expected 7 roles, found {len(roles)}"

    # Load all permissions
    perms = await db.permissions.find({}).to_list(length=None)

    discrepancies = []
    for perm in perms:
        perm_id = perm["permissionId"]
        module = perm.get("module")
        for role_id, expected_scope in DEFAULT_SCOPES.items():
            # Determine if a mapping should exist according to the approved matrix
            should_exist = True
            if role_id == "accounts":
                # Accounts only gets permissions from allowed modules and not excluded ones
                if module not in ACCOUNTS_ALLOWED_MODULES or perm_id in EXCLUDED_FOR_ACCOUNTS:
                    should_exist = False
            # All other roles get every permission
            if should_exist:
                # Expected scope may differ for accounts (COMPANY) or others via DEFAULT_SCOPES
                exp_scopes = [expected_scope]
                if role_id == "manager":
                    manager_self_and_team = {
                        "attendance.read", "attendance.manage", "attendance.sync",
                        "leave.read", "leave.apply", "leave.approve",
                        "reimbursement.read", "reimbursement.create", "reimbursement.approve",
                        "employee.read", "payroll.salary.read", "payroll.pf.read", "payroll.esi.read"
                    }
                    if perm_id in manager_self_and_team:
                        exp_scopes = ["SELF", "TEAM"]

                mapping = await db.role_permissions.find_one({"roleId": role_id, "permissionId": perm_id})
                if not mapping:
                    discrepancies.append(f"Missing mapping: role={role_id}, perm={perm_id}")
                else:
                    actual_scopes = mapping.get("scopes", [])
                    if set(actual_scopes) != set(exp_scopes):
                        discrepancies.append(
                            f"Scope mismatch: role={role_id}, perm={perm_id}, expected={exp_scopes}, got={actual_scopes}"
                        )
            else:
                mapping = await db.role_permissions.find_one({"roleId": role_id, "permissionId": perm_id})
                if mapping:
                    discrepancies.append(f"Unauthorized mapping: role={role_id}, perm={perm_id}")

    # Report all discrepancies as a single assertion failure for clarity
    assert not discrepancies, "Matrix discrepancies detected:\n" + "\n".join(discrepancies)

@pytest.mark.asyncio
async def test_versioning_and_history(setup_db):
    db = setup_db
    # All mappings created by the seed should have version == 1 and an ADD history entry
    mappings = await db.role_permissions.find({}).to_list(length=None)
    for m in mappings:
        assert m.get("version") == 1, f"Mapping version not 1 for {m['roleId']}/{m['permissionId']}"
        # Verify corresponding history entry
        hist = await db.role_permission_history.find_one({
            "roleId": m["roleId"],
            "permissionId": m["permissionId"],
            "changeType": "ADD",
        })
        assert hist is not None, f"Missing ADD history for {m['roleId']}/{m['permissionId']}"
        # Verify that the stored history array matches the mapping's scopes array (Model B).
        assert hist.get("newScopes") == m.get("scopes"), (
            f"History newScopes {hist.get('newScopes')!r} does not match "
            f"mapping scopes {m.get('scopes')!r} for {m['roleId']}/{m['permissionId']}"
        )
        assert hist.get("version") == 1

    # Rerun the seed to ensure no new versions or duplicate histories are created
    result = await seed_roles_and_mappings(db)
    assert result["created_mappings"] == 0, "Rerun created new mappings unexpectedly"
    assert result["added_history"] == 0, "Rerun added history entries unexpectedly"

    # Ensure existing history entries remain unchanged (immutable)
    total_history = await db.role_permission_history.count_documents({})
    # Expected history count = number of created mappings (from first seed)
    expected_history = len(mappings)
    assert total_history == expected_history, f"History count altered after reseed: expected {expected_history}, got {total_history}"
