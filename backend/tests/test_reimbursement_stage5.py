import asyncio
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.dependencies import get_current_user, get_database
# Simple async in‑memory mock collections (replicated from Phase 1 tests)
from backend.tests.mock_db import _MockClient
from app.role.engine.seed_roles import seed_roles_and_mappings
from app.permission.engine.seed_permissions import seed_permissions

# Mock database and user overrides

_mock_db_instance = None

def get_mock_db():
    global _mock_db_instance
    if _mock_db_instance is None:
        client = _MockClient()
        _mock_db_instance = client["ess_test"]
    return _mock_db_instance

async def seed_mock_data(db):
    await seed_permissions(db)
    await seed_roles_and_mappings(db)

def override_get_current_user_self():
    # User with role "employee" which has SELF scoped reimbursement permissions
    return {
        "empId": "emp123",
        "employeeId": "emp123",
        "roleId": "employee",
        "companyId": "compA",
        "branchId": "branchA",
        "employment": {"companyId": "compA", "branchId": "branchA"},
    }

def override_get_current_user_no_perm():
    # Same user but role that lacks reimbursement.create/read (use a role that doesn't have those perms)
    return {
        "empId": "emp123",
        "employeeId": "emp123",
        "roleId": "no_perm_role",
        "companyId": "compA",
        "branchId": "branchA",
        "employment": {"companyId": "compA", "branchId": "branchA"},
    }

def override_get_current_user_missing_role():
    return {
        "empId": "emp123",
        "employeeId": "emp123",
        # roleId missing on purpose
        "companyId": "compA",
        "branchId": "branchA",
        "employment": {"companyId": "compA", "branchId": "branchA"},
    }

# Apply overrides for the test client
app.dependency_overrides[get_current_user] = override_get_current_user_self
app.dependency_overrides[get_database] = get_mock_db
client = TestClient(app)

@pytest.fixture(autouse=True)
async def setup_mock_db():
    db = get_mock_db()
    # Ensure clean state
    await db.roles.delete_many({})
    await db.permissions.delete_many({})
    await db.role_permissions.delete_many({})
    await db.role_permission_history.delete_many({})
    # Seed base permissions and role mappings
    await seed_mock_data(db)
    # Ensure employee role exists (in case seed_roles_and_mappings did not create it)
    await db.roles.insert_one({"roleId": "employee", "name": "Employee", "isActive": True})
    # Clear RBAC permission cache to reflect seeded data
    from app.rbac.engine import _ROLE_PERM_CACHE
    _ROLE_PERM_CACHE.clear()
    # Insert mock employee document for the current user
    await db.employees.insert_one({
        "employeeId": "emp123",
        "empId": "emp123",
        "companyId": "compA",
        "branchId": "branchA",
        "managerId": "emp_manager",
        "employment": {"companyId": "compA", "branchId": "branchA"},
    })
    
    # Seed trip allowance policy to avoid 400 Bad Request
    await db.trip_allowance_policies.insert_one({
        "companyId": "compA",
        "policyCode": "TRIP_ALL_DEFAULT",
        "effectiveFrom": "2020-01-01",
        "effectiveTo": None,
        "allowedTripTypes": ["LOCAL", "OUTSTATION"],
        "ratePerKm": 10.0,
        "version": 1,
        "isActive": True
    })
    # Insert reimbursement permissions for employee role (SELF scope)
    from datetime import datetime
    await db.permissions.insert_one({
        "permissionId": "reimbursement.create",
        "name": "Create Reimbursement",
        "module": "reimbursement",
        "action": "create",
        "isActive": True,
        "createdAt": datetime.utcnow(),
        "version": 1,
    })
    await db.permissions.insert_one({
        "permissionId": "reimbursement.read",
        "name": "Read Reimbursement",
        "module": "reimbursement",
        "action": "read",
        "isActive": True,
        "createdAt": datetime.utcnow(),
        "version": 1,
    })
    employee_role_id = "employee"
    await db.role_permissions.insert_one({
        "roleId": employee_role_id,
        "permissionId": "reimbursement.create",
        "scope": "SELF",
        "isActive": True,
        "createdAt": datetime.utcnow(),
        "version": 1,
    })
    await db.role_permissions.insert_one({
        "roleId": employee_role_id,
        "permissionId": "reimbursement.read",
        "scope": "SELF",
        "isActive": True,
        "createdAt": datetime.utcnow(),
        "version": 1,
    })
    yield
    # Cleanup after tests
    await db.roles.delete_many({})
    await db.permissions.delete_many({})
    await db.role_permissions.delete_many({})
    await db.role_permission_history.delete_many({})
    await db.employees.delete_many({})
    await db.trip_allowance_policies.delete_many({})

@pytest.mark.asyncio
async def test_create_trip_sheet_success():
    payload = {
        "tripDate": "2023-01-01",
        "fromLocation": "A",
        "toLocation": "B",
        "tripType": "LOCAL",
        "startOdometer": 1000,
        "endOdometer": 1100,
        "claimedDistance": 100,
        "description": "Business trip"
    }
    response = client.post("/api/v2/reimbursement/trip-sheet", json=payload)
    if response.status_code != 200:
        print(f"DEBUG Response: {response.text}")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUBMITTED"
    assert "claimId" in data

@pytest.mark.asyncio
async def test_get_my_claims_success():
    # Assuming a claim was created in previous test, fetch it
    response = client.get("/api/v2/reimbursement/my-claims")
    assert response.status_code == 200
    claims = response.json()
    assert isinstance(claims, list)
    # At least one claim should be present for this employee
    assert any(c.get("employeeId") == "emp123" for c in claims)

@pytest.mark.asyncio
async def test_create_trip_sheet_no_permission():
    # Override user to a role without reimbursement permission
    app.dependency_overrides[get_current_user] = override_get_current_user_no_perm
    payload = {
        "tripDate": "2023-01-01",
        "fromLocation": "A",
        "toLocation": "B",
        "tripType": "LOCAL",
        "startOdometer": 1000,
        "endOdometer": 1100,
        "claimedDistance": 100,
        "description": "Business trip"
    }
    response = client.post("/api/v2/reimbursement/trip-sheet", json=payload)
    assert response.status_code == 403
    # Reset override for other tests
    app.dependency_overrides[get_current_user] = override_get_current_user_self

@pytest.mark.asyncio
async def test_get_my_claims_no_permission():
    app.dependency_overrides[get_current_user] = override_get_current_user_no_perm
    response = client.get("/api/v2/reimbursement/my-claims")
    assert response.status_code == 403
    app.dependency_overrides[get_current_user] = override_get_current_user_self

@pytest.mark.asyncio
async def test_missing_roleId():
    app.dependency_overrides[get_current_user] = override_get_current_user_missing_role
    response = client.get("/api/v2/reimbursement/my-claims")
    assert response.status_code == 403
    app.dependency_overrides[get_current_user] = override_get_current_user_self

# Independent TEAM scope evaluator test
@pytest.mark.asyncio
async def test_team_scope_evaluator():
    from app.rbac.engine import authorize
    db = get_mock_db()
    # Create target employee with managerId matching user empId
    await db.employees.insert_one({"employeeId": "emp_target", "managerId": "emp123"})
    user = override_get_current_user_self()
    # Seed a role permission with TEAM scope for a dummy permission
    await db.role_permissions.insert_one({"roleId": user["roleId"], "permissionId": "dummy.team", "scope": "TEAM"})
    await db.permissions.insert_one({"permissionId": "dummy.team"})
    # Should succeed when manager matches
    await authorize(user, "dummy.team", {"empId": "emp_target"})
    # Now test failure when manager mismatch
    await db.employees.insert_one({"employeeId": "emp_other", "managerId": "other_manager"})
    with pytest.raises(Exception) as exc:
        await authorize(user, "dummy.team", {"empId": "emp_other"})
    assert "TEAM scope violation" in str(exc.value)
