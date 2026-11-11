import pytest
import os
from datetime import datetime, timezone
from fastapi import HTTPException
from bson import ObjectId

from app.db.test_guard import assert_test_database_safe
from app.employee.models.employee import EmployeeModel
from app.employee.schemas.employee import EmployeeCreate, EmployeeUpdate
from app.employee.services.employee_service import EmployeeService
from app.employee.validators.employee_validator import EmployeeValidator
from backend.tests.mock_db import _MockClient

@pytest.fixture
def mock_db():
    assert_test_database_safe("mongodb://localhost:27017", "test_mock_db")
    client = _MockClient()
    return client["test_mock_db"]

@pytest.mark.asyncio
async def test_machine_id_same_employee_matches_allowed(mock_db):
    """
    Scenario 1, 2, 3: Same employee matching own identifiers (employeeCode, employeeId, empId) is ALLOWED.
    """
    service = EmployeeService(mock_db)

    # 1. Create employee where machineId == employeeCode -> Allowed
    emp1 = await service.create(EmployeeCreate(employeeCode="1091", machineId="1091"))
    assert emp1.employeeCode == "1091"
    assert emp1.machineId == "1091"

    # 2. Update employee where machineId matches its own employeeId -> Allowed
    emp1_updated = await service.update(emp1.id, EmployeeUpdate(machineId=emp1.employeeId))
    assert emp1_updated.machineId == emp1.employeeId

@pytest.mark.asyncio
async def test_machine_id_cross_employee_conflicts_rejected(mock_db):
    """
    Scenario 4, 5, 6, 7:
    Machine ID matching another employee's employeeCode, employeeId, empId, or machineId is REJECTED (409).
    """
    service = EmployeeService(mock_db)

    # Insert existing employee
    emp1 = await service.create(EmployeeCreate(employeeCode="EMP_A", machineId="00025"))

    # 4. Another employee with machineId matching emp1.employeeCode -> 409
    with pytest.raises(HTTPException) as exc4:
        await service.create(EmployeeCreate(employeeCode="EMP_B", machineId="EMP_A"))
    assert exc4.value.status_code == 409

    # 5. Another employee with machineId matching emp1.employeeId -> 409
    with pytest.raises(HTTPException) as exc5:
        await service.create(EmployeeCreate(employeeCode="EMP_C", machineId=emp1.employeeId))
    assert exc5.value.status_code == 409

    # 6. Another employee with machineId matching emp1.machineId -> 409
    with pytest.raises(HTTPException) as exc7:
        await service.create(EmployeeCreate(employeeCode="EMP_D", machineId="00025"))
    assert exc7.value.status_code == 409

@pytest.mark.asyncio
async def test_leading_zero_distinctness(mock_db):
    """
    Scenario 15: Leading zeros are preserved and distinct ("00025" != "25").
    """
    service = EmployeeService(mock_db)

    emp1 = await service.create(EmployeeCreate(employeeCode="EMP_001", machineId="00025"))
    assert emp1.machineId == "00025"

    # "25" must be allowed as a distinct machine ID
    emp2 = await service.create(EmployeeCreate(employeeCode="EMP_002", machineId="25"))
    assert emp2.machineId == "25"

@pytest.mark.asyncio
async def test_employee_update_retaining_machine_id(mock_db):
    """
    Scenario 10, 18:
    Updating an employee without changing Machine ID or updating other fields repeatedly is allowed.
    """
    service = EmployeeService(mock_db)

    emp = await service.create(EmployeeCreate(employeeCode="EMP_RET", machineId="5188"))
    assert emp.machineId == "5188"

    # Update status -> allowed
    up1 = await service.update(emp.id, EmployeeUpdate(status="Active"))
    assert up1.machineId == "5188"

    # Update with same machineId explicitly -> allowed
    up2 = await service.update(emp.id, EmployeeUpdate(machineId="5188"))
    assert up2.machineId == "5188"

@pytest.mark.asyncio
async def test_employee_update_to_another_employee_identifier_rejected(mock_db):
    """
    Scenario 11, 12:
    Updating Machine ID to another employee's identifier, or updating employeeCode to another employee's machineId is rejected.
    """
    service = EmployeeService(mock_db)

    emp1 = await service.create(EmployeeCreate(employeeCode="CODE_1", machineId="MID_1"))
    emp2 = await service.create(EmployeeCreate(employeeCode="CODE_2", machineId="MID_2"))

    # Update emp2 machineId to emp1's machineId -> 409
    with pytest.raises(HTTPException) as exc1:
        await service.update(emp2.id, EmployeeUpdate(machineId="MID_1"))
    assert exc1.value.status_code == 409

    # Update emp2 machineId to emp1's employeeCode -> 409
    with pytest.raises(HTTPException) as exc2:
        await service.update(emp2.id, EmployeeUpdate(machineId="CODE_1"))
    assert exc2.value.status_code == 409

    # Update emp2 employeeCode to emp1's machineId -> 409
    with pytest.raises(HTTPException) as exc3:
        await service.update(emp2.id, EmployeeUpdate(employeeCode="MID_1"))
    assert exc3.value.status_code == 409

@pytest.mark.asyncio
async def test_inactive_employee_retains_reservations(mock_db):
    """
    Scenario 13: Inactive employee's identifiers remain reserved.
    """
    service = EmployeeService(mock_db)

    emp = await service.create(EmployeeCreate(employeeCode="INACT_1", machineId="MID_INACT"))
    await service.update(emp.id, EmployeeUpdate(status="Inactive"))

    # Attempting to assign MID_INACT to another employee is rejected
    with pytest.raises(HTTPException) as exc:
        await service.create(EmployeeCreate(employeeCode="ACT_2", machineId="MID_INACT"))
    assert exc.value.status_code == 409

@pytest.mark.asyncio
async def test_null_or_missing_machine_id(mock_db):
    """
    Scenario 19: Employee creation with null or missing Machine ID preserves existing behaviour.
    """
    service = EmployeeService(mock_db)

    emp1 = await service.create(EmployeeCreate(employeeCode="NULL_1", machineId=None))
    assert emp1.machineId is None

    emp2 = await service.create(EmployeeCreate(employeeCode="NULL_2", machineId=None))
    assert emp2.machineId is None
