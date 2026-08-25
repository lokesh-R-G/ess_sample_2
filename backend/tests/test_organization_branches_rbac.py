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
    
    # Insert some mock branches
    await db.branchs.insert_one({"branchId": "b1", "companyId": "COMP123", "name": "Branch 1", "deletedAt": None})
    await db.branchs.insert_one({"branchId": "b2", "companyId": "COMP123", "name": "Branch 2", "deletedAt": None})
    await db.branchs.insert_one({"branchId": "b3", "companyId": "OTHER_COMP", "name": "Branch 3", "deletedAt": None})
    
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

async def override_manager_comp123():
    return get_mock_user("manager", scope="TEAM", company_id="COMP123")

async def override_manager_other():
    return get_mock_user("manager", scope="TEAM", company_id="OTHER_COMP")

@pytest.fixture
async def override_dependencies():
    db = await setup_mock_db()
    app.dependency_overrides[get_database] = lambda: db
    yield
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_organization_branches_rbac(override_dependencies):
    # Test Admin (Allowed to fetch any company's branches due to GLOBAL scope)
    app.dependency_overrides[get_current_user] = override_admin
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res1 = await ac.get("/api/v2/organization/branches/?companyId=COMP123")
        assert res1.status_code == 200
        assert len(res1.json()["data"]) == 2
        
        res2 = await ac.get("/api/v2/organization/branches/?companyId=OTHER_COMP")
        assert res2.status_code == 200
        assert len(res2.json()["data"]) == 1

    # Test Manager from COMP123
    app.dependency_overrides[get_current_user] = override_manager_comp123
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Can fetch their own company's branches
        res1 = await ac.get("/api/v2/organization/branches/?companyId=COMP123")
        assert res1.status_code == 200
        assert len(res1.json()["data"]) == 2
        
        # Cannot fetch another company's branches (manager doesn't have GLOBAL scope)
        res2 = await ac.get("/api/v2/organization/branches/?companyId=OTHER_COMP")
        assert res2.status_code == 403
        
    # Test Manager from OTHER_COMP
    app.dependency_overrides[get_current_user] = override_manager_other
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Cannot fetch COMP123 branches
        res1 = await ac.get("/api/v2/organization/branches/?companyId=COMP123")
        assert res1.status_code == 403
        
        # Can fetch their own company's branches
        res2 = await ac.get("/api/v2/organization/branches/?companyId=OTHER_COMP")
        assert res2.status_code == 200
        assert len(res2.json()["data"]) == 1
