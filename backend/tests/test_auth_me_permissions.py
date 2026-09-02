import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.mongo import get_database

@pytest.fixture
def test_app():
    return app

@pytest.fixture
def mock_db():
    from tests.mock_db import _MockDatabase
    return _MockDatabase()

@pytest.fixture
def app_client(test_app, mock_db):
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

@pytest.mark.asyncio
async def test_auth_me_returns_permissions(app_client, mock_db):
    from app.core.security import create_access_token
    from app.permission.engine.seed_permissions import seed_permissions
    from app.role.engine.seed_roles import seed_roles_and_mappings
    from app.rbac.engine import _ROLE_PERM_CACHE
    _ROLE_PERM_CACHE.clear()

    await seed_permissions(mock_db)
    await seed_roles_and_mappings(mock_db)

    await mock_db.users.insert_one({
        "empId": "test",
        "roleId": "admin",
        "role": "Admin",
        "firstLogin": False,
        "isActive": True
    })

    async with AsyncClient(transport=ASGITransport(app=app_client), base_url="http://test") as ac:
        token = create_access_token({"sub": "test", "empId": "test", "roleId": "admin"})
        resp = await ac.get(
            "/api/v1/auth/me/",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert "permissions" in data
        assert isinstance(data["permissions"], dict)
        assert "attendance.sync" in data["permissions"]
        assert "GLOBAL" in data["permissions"]["attendance.sync"]
