import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI, Depends
from app.dependencies import get_current_user, require_permission
from app.db.mongo import get_database

pytestmark = pytest.mark.asyncio

@pytest.fixture
def mock_db():
    from tests.mock_db import _MockClient
    return _MockClient()["ess_test"]

@pytest.fixture
def app_client(mock_db):
    test_app = FastAPI()

    test_app.dependency_overrides[get_database] = lambda: mock_db
    
    from app.scheduler.routes.router import router
    test_app.include_router(router)
    
    import app.rbac.engine
    import app.dependencies as deps
    orig_engine_get_db = app.rbac.engine.get_database
    orig_deps_get_db = deps.get_database
    
    app.rbac.engine.get_database = lambda: mock_db
    deps.get_database = lambda: mock_db
    
    yield test_app
    
    app.rbac.engine.get_database = orig_engine_get_db
    deps.get_database = orig_deps_get_db
    test_app.dependency_overrides.clear()

async def test_scheduler_auth(app_client, mock_db):
    from app.core.security import create_access_token
    from app.permission.engine.seed_permissions import seed_permissions
    from app.role.engine.seed_roles import seed_roles_and_mappings
    from app.rbac.engine import _ROLE_PERM_CACHE
    _ROLE_PERM_CACHE.clear()
    
    await seed_permissions(mock_db)
    await seed_roles_and_mappings(mock_db)
    
    await mock_db.users.insert_one({
        "empId": "test",
        "roleId": "employee",
        "isActive": True
    })
    
    # 1. Unauthenticated -> 401
    async with AsyncClient(transport=ASGITransport(app=app_client), base_url="http://test") as ac:
        resp = await ac.get("/config")
        assert resp.status_code == 401, f"Expected 401, got {resp.status_code}"
        
        # 2. Roles mapping testing
        for role in ["employee", "manager", "accounts"]:
            await mock_db.users.update_one({"empId": "test"}, {"$set": {"roleId": role}})
            token = create_access_token({"sub": "test", "empId": "test", "roleId": role})
            resp = await ac.get(
                "/config", 
                headers={"Authorization": f"Bearer {token}"}
            )
            assert resp.status_code == 403, f"Expected 403 for {role}, got {resp.status_code}"
            
        for role in ["hr", "admin", "accounts_md", "super_admin"]:
            await mock_db.users.update_one({"empId": "test"}, {"$set": {"roleId": role}})
            token = create_access_token({"sub": "test", "empId": "test", "roleId": role})
            resp = await ac.get(
                "/config", 
                headers={"Authorization": f"Bearer {token}"}
            )
            assert resp.status_code not in (401, 403), f"Expected authorization ALLOW for {role}, got {resp.status_code}"
