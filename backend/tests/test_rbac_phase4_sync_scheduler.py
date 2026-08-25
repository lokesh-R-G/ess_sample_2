import pytest
from app.rbac.engine import authorize
from fastapi import HTTPException

pytestmark = pytest.mark.asyncio

async def test_audit_attendance_sync_and_scheduler():
    from tests.mock_db import _MockClient
    _mock_client = _MockClient()
    db = _mock_client["ess_test"]
    
    # Ensure seed is applied
    from app.main import app
    from app.db.mongo import get_database
    
    app.dependency_overrides[get_database] = lambda: db
    
    from app.permission.engine.seed_permissions import seed_permissions
    from app.role.engine.seed_roles import seed_roles_and_mappings
    from app.rbac.engine import _ROLE_PERM_CACHE
    _ROLE_PERM_CACHE.clear()
    
    await seed_permissions(db)
    await seed_roles_and_mappings(db)

    # Scenarios: (role, attendance_sync_expected, scheduler_config_expected)
    # Testing for GLOBAL access
    scenarios = [
        ("admin", True, True),
        ("hr", True, True),
        ("super_admin", True, True),
        ("accounts_md", True, True),
        ("employee", False, False),
        ("manager", False, False),
        ("accounts", False, False)
    ]
    
    for role, exp_sync, exp_sched in scenarios:
        # Check attendance.sync
        try:
            await authorize({"roleId": role, "empId": "test"}, "attendance.sync", {})
            assert exp_sync, f"Expected {role} to be denied attendance.sync but was allowed"
        except HTTPException as e:
            if e.status_code == 403:
                assert not exp_sync, f"Expected {role} to be allowed attendance.sync but was denied"
            else:
                raise

        # Check scheduler.configure
        try:
            await authorize({"roleId": role, "empId": "test"}, "scheduler.configure", {})
            assert exp_sched, f"Expected {role} to be denied scheduler.configure but was allowed"
        except HTTPException as e:
            if e.status_code == 403:
                assert not exp_sched, f"Expected {role} to be allowed scheduler.configure but was denied"
            else:
                raise

