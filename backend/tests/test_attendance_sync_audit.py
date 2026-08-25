import pytest
from app.dependencies import require_permission
from app.rbac.engine import authorize

pytestmark = pytest.mark.asyncio

async def test_audit_attendance_sync():
    from tests.mock_db import _MockClient
    _mock_client = _MockClient()
    db = _mock_client["ess_test"]
    
    # Ensure seed is applied
    from app.permission.engine.seed_permissions import seed_permissions
    from app.role.engine.seed_roles import seed_roles_and_mappings
    await seed_permissions(db)
    await seed_roles_and_mappings(db)

    # Scenarios for attendance.sync (GLOBAL context)
    scenarios = [
        ("admin", True),
        ("hr", True),
        ("super_admin", True),
        ("accounts_md", True),
        ("employee", False),
        ("manager", False),
        ("accounts", False)
    ]
    
    print("\n--- Attendance Sync Audit ---")
    for role, expected_allow in scenarios:
        # Check attendance.sync
        try:
            await authorize({"roleId": role, "empId": "test"}, "attendance.sync", {})
            result = True
        except Exception:
            result = False
        print(f"{role} -> attendance.sync -> {'ALLOW' if result else 'DENY'} (Expected: {'ALLOW' if expected_allow else 'DENY'})")

    print("\n--- Scheduler Config (organization.manage) Audit ---")
    for role, expected_allow in scenarios:
        # Check organization.manage (as currently used by scheduler)
        try:
            await authorize({"roleId": role, "empId": "test"}, "organization.manage", {})
            result = True
        except Exception:
            result = False
        print(f"{role} -> organization.manage -> {'ALLOW' if result else 'DENY'} (Expected: {'ALLOW' if expected_allow else 'DENY'})")
