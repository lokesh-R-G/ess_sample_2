import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.mongo import get_database
from app.dependencies import get_current_user

# Mock dependencies
async def setup_mock_db():
    from backend.tests.mock_db import _MockClient
    from app.role.engine.seed_roles import seed_roles_and_mappings
    from app.permission.engine.seed_permissions import seed_permissions
    client = _MockClient()
    db = client["ess_test"]
    # Ensure fresh state
    await db.role_permissions.delete_many({})
    await seed_permissions(db)
    await seed_roles_and_mappings(db)
    return db

def get_mock_user(role: str, scope: str = "GLOBAL", company_id: str = "COMP123", employee_id: str = "EMP1"):
    return {
        "empId": employee_id,
        "employeeId": employee_id,
        "role": role,
        "roleId": role,
        "companyId": company_id
    }

async def override_admin():
    return get_mock_user("admin")

async def override_employee():
    return get_mock_user("employee", scope="SELF")

async def override_manager():
    return get_mock_user("manager", scope="TEAM")

async def override_accounts():
    return get_mock_user("accounts", scope="COMPANY", company_id="COMP123")

@pytest.fixture
async def override_dependencies():
    db = await setup_mock_db()
    app.dependency_overrides[get_database] = lambda: db
    yield
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_payroll_cycle_create_rbac(override_dependencies):
    # Test Admin (Allowed)
    app.dependency_overrides[get_current_user] = override_admin
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v2/payroll/cycles", json={
            "name": "Test Cycle",
            "startDate": "2026-08-01T00:00:00",
            "endDate": "2026-08-31T23:59:59"
        })
        assert response.status_code == 200

    # Test Employee (Forbidden)
    app.dependency_overrides[get_current_user] = override_employee
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v2/payroll/cycles", json={
            "name": "Test Cycle",
            "startDate": "2026-08-01T00:00:00",
            "endDate": "2026-08-31T23:59:59"
        })
        assert response.status_code == 403
        
    # Test Manager (Forbidden)
    app.dependency_overrides[get_current_user] = override_manager
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v2/payroll/cycles", json={
            "name": "Test Cycle",
            "startDate": "2026-08-01T00:00:00",
            "endDate": "2026-08-31T23:59:59"
        })
        assert response.status_code == 403

    # Test Accounts (Forbidden)
    app.dependency_overrides[get_current_user] = override_accounts
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v2/payroll/cycles", json={
            "name": "Test Cycle",
            "startDate": "2026-08-01T00:00:00",
            "endDate": "2026-08-31T23:59:59"
        })
        assert response.status_code == 403

@pytest.mark.asyncio
async def test_payroll_cycle_list_rbac(override_dependencies):
    # Test Admin (Allowed to read)
    app.dependency_overrides[get_current_user] = override_admin
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # We also pass companyId to prove it does not affect the route resolving or error out
        response = await ac.get("/api/v2/payroll/cycles?companyId=XYZ")
        assert response.status_code == 200
        
    # Employee, Manager should be forbidden (since read cycles is global)
    app.dependency_overrides[get_current_user] = override_employee
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v2/payroll/cycles")
        assert response.status_code == 403
