import pytest
import asyncio
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, patch, MagicMock

from app.salary.repositories.employee_salary_component_repository import EmployeeSalaryComponentRepository
from app.payroll.services.salary_assignment_service import SalaryAssignmentService
from app.payroll.services.payroll_calculation_service import PayrollCalculationEngine
from app.domain_models import EmployeeSalaryComponent

@pytest.fixture
def mock_db():
    db = MagicMock()
    collections = {}
    def get_collection(name):
        if name not in collections:
            collections[name] = AsyncMock()
        return collections[name]
    db.__getitem__.side_effect = get_collection
    return db

@pytest.mark.asyncio
async def test_salary_resolver_boundaries(mock_db):
    repo = EmployeeSalaryComponentRepository(mock_db)
    
    mock_cursor = AsyncMock()
    v1_date = datetime(2026, 1, 1, tzinfo=timezone.utc)
    v2_date = datetime(2026, 1, 15, tzinfo=timezone.utc)
    
    mock_cursor.to_list.return_value = [
        {
            "_id": "v2_id",
            "employeeId": "EMP001",
            "salaryComponentId": "BASIC",
            "version": 2,
            "effectiveFrom": v2_date,
            "effectiveTo": None,
            "isCurrent": True
        },
        {
            "_id": "v1_id",
            "employeeId": "EMP001",
            "salaryComponentId": "BASIC",
            "version": 1,
            "effectiveFrom": v1_date,
            "effectiveTo": v2_date,
            "isCurrent": False
        }
    ]
    mock_db["employee_salary_components"].find = MagicMock(return_value=mock_cursor)
    
    result = await repo.get_components_by_employee_and_date("EMP001", v2_date + timedelta(days=1))
    
    assert len(result) == 1
    assert result[0]["version"] == 2
    assert result[0]["_id"] == "v2_id"

def test_distribution_ratio_calculation():
    components = [
        {"id": "BASIC", "monthlyAmount": 50000, "includeInGross": True, "attendanceDependent": True},
        {"id": "HRA", "monthlyAmount": 25000, "includeInGross": True, "attendanceDependent": True},
        {"id": "FIXED_ALLOWANCE", "monthlyAmount": 5000, "includeInGross": True, "attendanceDependent": False}
    ]
    
    result = PayrollCalculationEngine.calculateDistributionRatios(components)
    basic = next(c for c in result if c["id"] == "BASIC")
    hra = next(c for c in result if c["id"] == "HRA")
    fixed = next(c for c in result if c["id"] == "FIXED_ALLOWANCE")
    
    assert abs(basic["distributionRatio"] - 0.6666) < 0.001
    assert abs(hra["distributionRatio"] - 0.3333) < 0.001
    assert fixed["distributionRatio"] == 0.0

def test_monthly_amount_is_canonical():
    components = [
        {"id": "BASIC", "amount": 100, "monthlyAmount": 50000, "includeInGross": True, "componentType": "Earning"}
    ]
    gross = PayrollCalculationEngine.calculateGross(components)
    assert gross == 50000

@pytest.mark.asyncio
async def test_salary_assignment_versioning(mock_db):
    service = SalaryAssignmentService(mock_db)
    mock_db["salary_structures"].find_one.return_value = {"_id": "507f1f77bcf86cd799439011", "componentIds": ["COMP1"]}
    
    mock_cursor = AsyncMock()
    mock_cursor.to_list.return_value = [
        {"_id": "COMP1", "name": "Basic", "calculationMethod": "Flat", "includeInGross": True}
    ]
    mock_db["salary_components"].find = MagicMock(return_value=mock_cursor)
    
    mock_db["employee_salary_components"].find_one.return_value = {"version": 1}
    mock_db["pf_rules"].find_one.return_value = None
    mock_db["esi_rules"].find_one.return_value = None
    
    empty_cursor = AsyncMock()
    empty_cursor.to_list.return_value = []
    mock_db["pt_slabs"].find = MagicMock(return_value=empty_cursor)
    
    payload = {
        "employeeId": "100100",
        "salaryStructureId": "507f1f77bcf86cd799439011",
        "basicSalary": 50000,
        "customComponents": {"COMP1": 50000},
        "effectiveFrom": "2026-09-01T00:00:00Z"
    }
    
    await service.assign_salary(payload)
    
    mock_db["employee_salary_components"].update_many.assert_called_once()
    call_args = mock_db["employee_salary_components"].update_many.call_args[0]
    assert call_args[0] == {"employeeId": "100100", "isCurrent": True}
    assert call_args[1]["$set"]["isCurrent"] is False
    assert call_args[1]["$set"]["status"] == "Archived"
    assert call_args[1]["$set"]["effectiveTo"] == datetime(2026, 9, 1, tzinfo=timezone.utc)
    
    mock_db["employee_salary_components"].insert_many.assert_called_once()
    insert_args = mock_db["employee_salary_components"].insert_many.call_args[0][0]
    
    assert len(insert_args) == 1
    new_comp = insert_args[0]
    assert new_comp["version"] == 2
    assert new_comp["isCurrent"] is True
    assert new_comp["effectiveTo"] is None
    assert new_comp["status"] == "Active"
    assert new_comp["monthlyAmount"] == 50000
    assert new_comp["effectiveFrom"] == datetime(2026, 9, 1, tzinfo=timezone.utc)


@pytest.mark.asyncio
async def test_historical_payroll_resolution(mock_db):
    """
    Test Point 9: Historical Payroll resolution.
    July V1, August V2.
    Run July payroll in December -> MUST use July V1.
    """
    repo = EmployeeSalaryComponentRepository(mock_db)
    
    july_date = datetime(2026, 7, 1, tzinfo=timezone.utc)
    august_date = datetime(2026, 8, 1, tzinfo=timezone.utc)
    
    # December payroll run for a July cycle (cycle.startDate = July 1)
    target_date = july_date
    
    # We simulate the DB returning only the V1 component since the query is:
    # effectiveFrom <= target_date AND (effectiveTo == None OR effectiveTo > target_date)
    # V1 (July) matches because effectiveFrom(July) <= July AND effectiveTo(August) > July
    # V2 (August) fails because effectiveFrom(August) <= July is FALSE
    
    mock_cursor = AsyncMock()
    mock_cursor.to_list.return_value = [
        {
            "_id": "v1_id",
            "employeeId": "EMP001",
            "salaryComponentId": "BASIC",
            "version": 1,
            "effectiveFrom": july_date,
            "effectiveTo": august_date,
            "isCurrent": False,
            "monthlyAmount": 50000
        }
    ]
    mock_db["employee_salary_components"].find = MagicMock(return_value=mock_cursor)
    
    result = await repo.get_components_by_employee_and_date("EMP001", target_date)
    
    assert len(result) == 1
    assert result[0]["version"] == 1
    assert result[0]["monthlyAmount"] == 50000
