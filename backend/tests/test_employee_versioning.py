import pytest
import os
from datetime import datetime, timezone
from fastapi import HTTPException
from bson import ObjectId

from app.db.test_guard import assert_test_database_safe
from app.employee.models.employee import EmployeeModel
from app.employee.schemas.employee import EmployeeCreate, EmployeeUpdate
from app.employee.services.employee_service import EmployeeService
from backend.tests.mock_db import _MockClient

@pytest.fixture
def mock_db():
    assert_test_database_safe("mongodb://localhost:27017", "test_mock_db")
    client = _MockClient()
    return client["test_mock_db"]

@pytest.mark.asyncio
async def test_employee_versioning_and_company_uniqueness(mock_db):
    """
    Test that an employee can be created and version-updated without failing unique index
    on companyId + employeeCode.
    """
    service = EmployeeService(mock_db)

    # 1. Create employee in Tab 1 (companyId is not in Tab 1 payload)
    emp = await service.create(EmployeeCreate(employeeCode="1021", machineId="1021"))
    assert emp.employeeCode == "1021"
    assert emp.machineId == "1021"

    # 2. Update employee (e.g. status change or Tab 1 edit) -> creates version 2
    emp_v2 = await service.update(emp.id, EmployeeUpdate(status="Active"))
    assert emp_v2.employeeCode == "1021"

    # 3. Simulate another update -> creates version 3
    emp_v3 = await service.update(emp_v2.id, EmployeeUpdate(machineId="1021"))
    assert emp_v3.machineId == "1021"

