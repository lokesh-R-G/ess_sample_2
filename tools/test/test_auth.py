import asyncio
from fastapi import HTTPException
from app.rbac.engine import authorize
from app.role.engine.seed_roles import seed_roles_and_mappings
from app.permission.engine.seed_permissions import seed_permissions
from tests.mock_db import get_mock_db

async def run():
    db = get_mock_db()
    from app.rbac.engine import _ROLE_PERM_CACHE
    _ROLE_PERM_CACHE.clear()
    await seed_permissions(db)
    await seed_roles_and_mappings(db)

    user = {"roleId": "super_admin", "empId": "admin_emp1"}
    rc = {"empId": "admin_emp1"}

    try:
        await authorize(user, "attendance.read", rc)
        print("AUTHORIZE SUCCESS!")
    except HTTPException as e:
        print("AUTHORIZE FAILED:", e.detail)

asyncio.run(run())
