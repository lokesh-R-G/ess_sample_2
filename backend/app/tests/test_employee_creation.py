import pytest
import asyncio
from datetime import datetime
import mongomock_motor
from app.employee.services.employee_service import EmployeeService
from app.employee.schemas.employee import EmployeeCreate
from app.attendance_v2.routes.admin_attendance_routes import get_attendance_monitor

@pytest.fixture
def mock_db():
    client = mongomock_motor.AsyncMongoMockClient()
    return client["test_db"]

@pytest.mark.asyncio
async def test_concurrent_employee_creation(mock_db):
    db = mock_db
    # Reset counters for test
    await db.identity_counters.update_one({"_id": "employeeId"}, {"$set": {"sequence_value": 100000}}, upsert=True)
    
    svc = EmployeeService(db)
    
    # Create 5 employees concurrently
    async def create_emp(code: str):
        data = EmployeeCreate(employeeCode=code)
        # Mocking validator
        svc.validator.validate_create = lambda x: asyncio.sleep(0) 
        return await svc.create(data, "test_admin")

    # This ensures atomic generation works correctly without race conditions
    results = await asyncio.gather(*(create_emp(f"TEST_{i}") for i in range(5)))
    
    employee_ids = [getattr(r, "employeeId", r.get("employeeId") if isinstance(r, dict) else None) for r in results]
    employee_codes = [getattr(r, "employeeCode", r.get("employeeCode") if isinstance(r, dict) else None) for r in results]
    
    # Check uniqueness
    assert len(set(employee_ids)) == 5
    assert len(set(employee_codes)) == 5
    
    # Ensure they started at 100001
    assert "100001" in employee_ids
    assert "100005" in employee_ids
    
    # Check separation
    assert all([code.startswith("TEST_") for code in employee_codes])
    
    # Clean up
    await db.employees.delete_many({"employeeCode": {"$regex": "^TEST_"}})
