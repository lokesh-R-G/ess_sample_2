import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException
from app.holiday_calendar.routes.special_day_routes import _resolve_admin_company_id

@pytest.fixture
def mock_db():
    db = MagicMock()
    db.companies = MagicMock()
    db.companys = MagicMock()
    db.employees = MagicMock()
    db.employee_employment_histories = MagicMock()
    return db

@pytest.mark.asyncio
async def test_resolve_company_from_current_user(mock_db):
    user = {
        "empId": "5188",
        "companyId": "COMPANY_AUTH_123",
        "role": "Super Admin"
    }
    resolved = await _resolve_admin_company_id(user, None, mock_db)
    assert resolved == "COMPANY_AUTH_123"

@pytest.mark.asyncio
async def test_resolve_company_super_admin_override(mock_db):
    user = {
        "empId": "5188",
        "companyId": "COMPANY_AUTH_123",
        "role": "Super Admin"
    }
    mock_db.companies.find_one = AsyncMock(return_value={"_id": "COMPANY_TARGET_456", "name": "Target Company"})
    resolved = await _resolve_admin_company_id(user, "COMPANY_TARGET_456", mock_db)
    assert resolved == "COMPANY_TARGET_456"

@pytest.mark.asyncio
async def test_resolve_company_from_employment_history(mock_db):
    user = {
        "empId": "1001",
        "companyId": None,
        "employeeCode": "1001",
        "role": "Super Admin"
    }
    mock_db.employees.find.return_value.to_list = AsyncMock(return_value=[
        {"employeeId": "1001", "employeeCode": "1001"}
    ])
    mock_db.employee_employment_histories.find_one = AsyncMock(return_value={
        "employeeId": "1001",
        "companyId": "COMPANY_FROM_EH",
        "isCurrent": True
    })
    resolved = await _resolve_admin_company_id(user, None, mock_db)
    assert resolved == "COMPANY_FROM_EH"

@pytest.mark.asyncio
async def test_resolve_company_super_admin_fallback(mock_db):
    user = {
        "empId": "ADMIN_NEW",
        "companyId": None,
        "role": "Super Admin"
    }
    mock_db.employees.find.return_value.to_list = AsyncMock(return_value=[])
    mock_db.employee_employment_histories.find_one = AsyncMock(return_value=None)
    mock_db.companies.find_one = AsyncMock(return_value={"_id": "DEFAULT_ACTIVE_COMPANY", "name": "Default Company"})
    resolved = await _resolve_admin_company_id(user, None, mock_db)
    assert resolved == "DEFAULT_ACTIVE_COMPANY"

@pytest.mark.asyncio
async def test_resolve_company_employee_without_company_raises_400(mock_db):
    user = {
        "empId": "TEST_EMP_ORPHAN",
        "companyId": None,
        "role": "Employee"
    }
    mock_db.employees.find.return_value.to_list = AsyncMock(return_value=[])
    mock_db.employee_employment_histories.find_one = AsyncMock(return_value=None)
    
    with pytest.raises(HTTPException) as exc:
        await _resolve_admin_company_id(user, None, mock_db)
    assert exc.value.status_code == 400
    assert "Unable to resolve authorized company ID" in exc.value.detail
