import pytest
from fastapi import HTTPException

from app.db.test_guard import assert_test_database_safe
from app.employee.schemas.employee import EmployeeCreate, EmployeeUpdate
from app.employee.schemas.employment_history import EmploymentHistoryCreate
from app.employee.services.employee_service import EmployeeService
from app.employee.services.employment_history_service import EmploymentHistoryService
from backend.tests.mock_db import _MockClient


@pytest.fixture
def mock_db():
    assert_test_database_safe("mongodb://localhost:27017", "test_employee_company_scope")
    client = _MockClient()
    return client["test_employee_company_scope"]


@pytest.mark.asyncio
async def test_same_company_employee_code_conflict_rejected(mock_db):
    employee_service = EmployeeService(mock_db)
    history_service = EmploymentHistoryService(mock_db)

    emp_a = await employee_service.create(EmployeeCreate(employeeCode="1021", machineId="MID_A"))
    await history_service.create(EmploymentHistoryCreate(employeeId=str(emp_a.employeeId), companyId="company-1"))

    emp_b = await employee_service.create(EmployeeCreate(employeeCode="1021", machineId="MID_B"))

    with pytest.raises(HTTPException) as exc:
        await history_service.create(EmploymentHistoryCreate(employeeId=str(emp_b.employeeId), companyId="company-1"))

    assert exc.value.status_code == 409
    assert "employee code" in str(exc.value.detail).lower()


@pytest.mark.asyncio
async def test_cross_company_employee_code_allowed(mock_db):
    employee_service = EmployeeService(mock_db)
    history_service = EmploymentHistoryService(mock_db)

    emp_a = await employee_service.create(EmployeeCreate(employeeCode="1021", machineId="MID_A"))
    await history_service.create(EmploymentHistoryCreate(employeeId=str(emp_a.employeeId), companyId="company-1"))

    emp_b = await employee_service.create(EmployeeCreate(employeeCode="1021", machineId="MID_B"))
    second = await history_service.create(EmploymentHistoryCreate(employeeId=str(emp_b.employeeId), companyId="company-2"))

    assert second.employeeId == str(emp_b.employeeId)
    assert second.companyId == "company-2"


@pytest.mark.asyncio
async def test_temporal_employee_update_keeps_code_and_master_id(mock_db):
    employee_service = EmployeeService(mock_db)

    emp = await employee_service.create(EmployeeCreate(employeeCode="1021", machineId="MID_A"))
    original_master = emp.masterEmployeeId

    updated = await employee_service.update(emp.id, EmployeeUpdate(status="Active"))

    assert updated is not None
    assert updated.employeeCode == "1021"
    assert updated.masterEmployeeId == original_master
    assert updated.id != emp.id
