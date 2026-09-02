import asyncio
from httpx import AsyncClient, ASGITransport
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app as fastapi_app
from tests.mock_db import _MockDatabase
from app.core.security import create_access_token
from app.permission.engine.seed_permissions import seed_permissions
from app.role.engine.seed_roles import seed_roles_and_mappings
from app.rbac.engine import _ROLE_PERM_CACHE
import app.rbac.engine
import app.dependencies as deps

# Canonical roles
ROLES = [
    ("employee", "Employee"),
    ("manager", "Manager"),
    ("hr", "HR"),
    ("admin", "Admin"),
    ("accounts", "Accounts"),
    ("accounts_md", "Accounts MD"),
    ("super_admin", "Super Admin")
]

ENDPOINTS = [
    ("GET /api/v1/auth/me/", "GET", "/api/v1/auth/me/"),
    ("POST /api/v2/attendance/recalculate", "POST", "/api/v2/attendance/recalculate", {"fromDate": "2023-01-01", "toDate": "2023-01-31"}),
    ("GET /api/v2/scheduler/config", "GET", "/api/v2/scheduler/config"),
    ("PUT /api/v2/scheduler/config/ESSL_SHORT_SYNC", "PUT", "/api/v2/scheduler/config/ESSL_SHORT_SYNC", {"enabled": True, "frequencyMinutes": 15, "lookbackDays": 1})
]

async def run_matrix():
    mock_db = _MockDatabase()
    
    orig_engine_db = app.rbac.engine.get_database
    orig_deps_db = deps.get_database
    
    app.rbac.engine.get_database = lambda: mock_db
    deps.get_database = lambda: mock_db

    _ROLE_PERM_CACHE.clear()
    await seed_permissions(mock_db)
    await seed_roles_and_mappings(mock_db)

    # Seed users
    for role_id, role_name in ROLES:
        await mock_db.users.insert_one({
            "empId": f"usr_{role_id}",
            "roleId": role_id,
            "role": role_name,
            "isActive": True,
            "firstLogin": False
        })
        
    print(f"{'Role':<15} | {'Endpoint':<45} | Result")
    print("-" * 75)

    async with AsyncClient(transport=ASGITransport(app=fastapi_app), base_url="http://test") as ac:
        for role_id, role_name in ROLES:
            token = create_access_token({"sub": f"usr_{role_id}", "empId": f"usr_{role_id}", "roleId": role_id})
            headers = {"Authorization": f"Bearer {token}"}
            
            for name, method, url, *body in ENDPOINTS:
                payload = body[0] if body else None
                
                if method == "GET":
                    resp = await ac.get(url, headers=headers)
                elif method == "POST":
                    resp = await ac.post(url, headers=headers, json=payload)
                elif method == "PUT":
                    resp = await ac.put(url, headers=headers, json=payload)
                    
                status = resp.status_code
                res_str = "ALLOW" if status in [200, 201] else f"DENY ({status})"
                if status not in [200, 201, 401, 403]:
                    res_str = f"ALLOW (Failed: {status})" # It passed auth but failed logic
                
                print(f"{role_name:<15} | {name:<45} | {res_str}")
            print("-" * 75)

    app.rbac.engine.get_database = orig_engine_db
    deps.get_database = orig_deps_db

if __name__ == "__main__":
    asyncio.run(run_matrix())
