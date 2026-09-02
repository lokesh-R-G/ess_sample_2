import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__)))

import asyncio
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient

from app.db.mongo import get_database
from app.dependencies import get_current_user, require_permission
from app.rbac.context_providers import self_context
from tests.mock_db import get_mock_db

app = FastAPI()

@app.get("/api/v1/attendance/me/", dependencies=[Depends(require_permission("attendance.read", resource_context_provider=self_context))])
async def my_attendance(current_user=Depends(get_current_user)):
    return {"empId": current_user.get("empId")}

def override_super_admin():
    return {"empId": "admin1", "employeeId": "admin1", "roleId": "super_admin"}

app.dependency_overrides[get_database] = get_mock_db
app.dependency_overrides[get_current_user] = override_super_admin

if __name__ == "__main__":
    from app.role.engine.seed_roles import seed_roles_and_mappings
    from app.permission.engine.seed_permissions import seed_permissions
    db = get_mock_db()
    asyncio.run(seed_permissions(db))
    asyncio.run(seed_roles_and_mappings(db))
    
    from app.rbac.engine import _ROLE_PERM_CACHE
    _ROLE_PERM_CACHE.clear()

    client = TestClient(app)
    resp = client.get("/api/v1/attendance/me/")
    print(resp.status_code, resp.json())
