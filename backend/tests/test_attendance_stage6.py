import asyncio
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.dependencies import get_current_user, get_database
from backend.tests.mock_db import _MockClient
from app.role.engine.seed_roles import seed_roles_and_mappings
from app.permission.engine.seed_permissions import seed_permissions

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
    
    # Insert target employee for context provider lookups
    await db.employees.insert_one({
        "employeeId": "target_emp",
        "employeeCode": "target_emp",
        "managerId": "manager123",
        "branchId": "branchA",
        "companyId": "compA"
    })
    
    # Also add user for /my-data/ (needs to exist for the dict fetch)
    await db.users.insert_one({
        "empId": "target_emp",
        "lastSyncAt": None
    })

def override_target_self():
    return {"empId": "target_emp", "employeeId": "target_emp", "roleId": "employee"}

def override_target_team():
    return {"empId": "manager123", "employeeId": "manager123", "roleId": "manager"}

def override_target_branch():
    return {"empId": "branch_mgr", "employeeId": "branch_mgr", "roleId": "branch_manager", "branchId": "branchA"}

def override_target_company():
    return {"empId": "comp_admin", "employeeId": "comp_admin", "roleId": "accounts", "companyId": "compA"}

def override_global():
    return {"empId": "admin1", "employeeId": "admin1", "roleId": "admin"}

def override_super_admin():
    return {"empId": "admin1", "employeeId": "admin1", "roleId": "super_admin"}

def override_guest():
    return {"empId": "guest", "employeeId": "guest", "roleId": "guest"}

def override_no_perm():
    return {"empId": "guest", "employeeId": "guest", "roleId": "guest"}

from app.rbac.engine import _ROLE_PERM_CACHE

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    _ROLE_PERM_CACHE.clear()
    db = get_mock_db()
    asyncio.run(seed_mock_data(db))
    # Add explicit branch scope for our mock branch_manager role
    asyncio.run(db.role_permissions.insert_one({
        "roleId": "branch_manager",
        "permissionId": "attendance.read",
        "scope": "BRANCH",
        "isActive": True
    }))

def _run_with_user(override_func, test_func):
    print('TEST_ATTENDANCE DB ID:', id(get_mock_db()))
    from app.rbac.engine import _get_db as get_db_func
    print('_GET_DB OVERRIDE RESOLVED:', id(get_db_func()))
    app.dependency_overrides[get_database] = get_mock_db
    app.dependency_overrides[get_current_user] = override_func
    client = TestClient(app)
    try:
        test_func(client)
    finally:
        app.dependency_overrides.pop(get_current_user, None)
        # We don't strictly need to pop get_database, but it's cleaner to re-assign it.

# --- GET /attendance/me/ ---
def test_attendance_me_self():
    def _test(client):
        resp = client.get("/api/v1/attendance/me/")
        assert resp.status_code == 200
        assert resp.json()["empId"] == "target_emp"
    _run_with_user(override_target_self, _test)

def test_attendance_me_no_perm():
    def _test(client):
        resp = client.get("/api/v1/attendance/me/")
        assert resp.status_code == 403
    _run_with_user(override_no_perm, _test)


# --- GET /attendance/{emp_id}/ ---
def test_attendance_by_emp_self():
    def _test(client):
        resp = client.get("/api/v1/attendance/target_emp/")
        assert resp.status_code == 200
    _run_with_user(override_target_self, _test)

def test_attendance_by_emp_team():
    def _test(client):
        resp = client.get("/api/v1/attendance/target_emp/")
        assert resp.status_code == 200
    _run_with_user(override_target_team, _test)

def test_attendance_by_emp_branch():
    def _test(client):
        resp = client.get("/api/v1/attendance/target_emp/")
        assert resp.status_code == 200
    _run_with_user(override_target_branch, _test)

def test_attendance_by_emp_company():
    def _test(client):
        resp = client.get("/api/v1/attendance/target_emp/")
        assert resp.status_code == 200
    _run_with_user(override_target_company, _test)

def test_attendance_by_emp_global():
    def _test(client):
        resp = client.get("/api/v1/attendance/target_emp/")
        assert resp.status_code == 200
    _run_with_user(override_global, _test)

def test_attendance_by_emp_no_perm():
    def _test(client):
        resp = client.get("/api/v1/attendance/target_emp/")
        assert resp.status_code == 403
    _run_with_user(override_no_perm, _test)


# --- POST /sync/essl/ ---
def test_sync_essl_global():
    def _test(client):
        # We mock sync_essl_logs to just return success in the DB so we don't hit real ESSL
        pass
        
    # Wait, the endpoint calls sync_essl_logs which does external network.
    # To prevent that, we can monkeypatch.
    # Actually, if we just care about authorization, it might fail inside. Let's see.
    pass

# We will actually run a test that monkeypatches the service
def test_sync_essl_auth(monkeypatch):
    from app.api.routes.sync import sync_essl_logs
    async def mock_sync(*args, **kwargs):
        return {"status": "success"}
    monkeypatch.setattr("app.api.routes.sync.sync_essl_logs", mock_sync)
    
    def _test_global(client):
        resp = client.post("/api/v1/sync/essl/", json={"fromDate": "2026-01-01", "toDate": "2026-01-31"})
        assert resp.status_code == 200
    _run_with_user(override_global, _test_global)
    
    def _test_company(client):
        resp = client.post("/api/v1/sync/essl/", json={"fromDate": "2026-01-01", "toDate": "2026-01-31"})
        assert resp.status_code == 403
    _run_with_user(override_target_company, _test_company)


# --- POST /sync/my-data/ ---
def test_sync_my_data_self(monkeypatch):
    async def mock_schedule(*args, **kwargs):
        pass
    monkeypatch.setattr("app.api.routes.sync.schedule_user_sync_now", mock_schedule)
    
    def _test(client):
        resp = client.post("/api/v1/sync/my-data/")
        assert resp.status_code == 200
        assert resp.json()["empId"] == "target_emp"
    _run_with_user(override_target_self, _test)

def test_sync_my_data_no_perm(monkeypatch):
    def _test(client):
        resp = client.post("/api/v1/sync/my-data/")
        assert resp.status_code == 403
    _run_with_user(override_no_perm, _test)
