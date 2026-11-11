import pytest
import os
from datetime import datetime, timezone
from fastapi import HTTPException
from pydantic import ValidationError

from app.db.test_guard import assert_test_database_safe
from app.employee.models.employee import EmployeeModel
from app.employee.schemas.employee import EmployeeCreate, EmployeeUpdate
from app.employee.validators.employee_validator import EmployeeValidator
from backend.tests.mock_db import _MockClient

@pytest.fixture
def mock_db():
    assert_test_database_safe("mongodb://localhost:27017", "test_mock_db")
    client = _MockClient()
    return client["test_mock_db"]

@pytest.mark.asyncio
async def test_machine_id_uniqueness_on_create(mock_db):
    validator = EmployeeValidator(mock_db)
    
    # 1. Insert an existing employee with machineId "00025"
    await mock_db.employees.insert_one({
        "employeeId": "1001",
        "employeeCode": "EMP101",
        "machineId": "00025",
        "status": "Active",
        "deletedAt": None
    })
    
    # 2. Attempt to create another employee with same machineId "00025" -> must fail with 409
    with pytest.raises(HTTPException) as exc_info:
        await validator.validate_create(EmployeeCreate(employeeCode="EMP102", machineId="00025"))
    assert exc_info.value.status_code == 409
    assert "00025" in exc_info.value.detail

    # 3. Create employee with different machineId "25" (leading zero difference) -> must succeed!
    await validator.validate_create(EmployeeCreate(employeeCode="EMP103", machineId="25"))

@pytest.mark.asyncio
async def test_machine_id_uniqueness_against_inactive_employee(mock_db):
    validator = EmployeeValidator(mock_db)
    
    # Inactive employee has machineId "00088"
    await mock_db.employees.insert_one({
        "employeeId": "1002",
        "employeeCode": "EMP102",
        "machineId": "00088",
        "status": "Inactive",
        "deletedAt": None
    })
    
    # Attempting to assign "00088" to another employee must be rejected
    with pytest.raises(HTTPException) as exc_info:
        await validator.validate_create(EmployeeCreate(employeeCode="EMP104", machineId="00088"))
    assert exc_info.value.status_code == 409

@pytest.mark.asyncio
async def test_machine_id_partial_update_retains_value(mock_db):
    validator = EmployeeValidator(mock_db)
    
    # Existing employee has machineId "00099"
    await mock_db.employees.insert_one({
        "employeeId": "1005",
        "employeeCode": "EMP105",
        "machineId": "00099",
        "status": "Active",
        "deletedAt": None
    })
    
    # Self update with same machineId -> succeeds
    await validator.validate_update("1005", EmployeeUpdate(machineId="00099"))
    
    # Partial update omitting machineId -> machineId is None in model_dump(exclude_unset=True), validator passes
    await validator.validate_update("1005", EmployeeUpdate(status="Inactive"))

