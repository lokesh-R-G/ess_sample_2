import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.reporting_hierarchy_service import get_reporting_employee_ids, get_manager_identifiers
from app.approval.repositories.approval_repository import ApprovalRepository
from app.approval.services.approval_service import ApprovalService

class AsyncIter:
    def __init__(self, items):
        self.items = items

    async def __aiter__(self):
        for item in self.items:
            yield item

@pytest.mark.asyncio
async def test_reporting_hierarchy_service():
    mock_db = MagicMock()
    
    # Manager emp record
    mgr_doc = {"_id": "mgr_obj_id_123", "employeeId": "EMP_MGR_001", "employeeCode": "5188"}
    
    # db.employees.find returns an async iterable
    mock_db.employees.find.return_value = AsyncIter([mgr_doc])
    
    cursor_mock = MagicMock()
    cursor_mock.to_list = AsyncMock(return_value=[
        {"employeeId": "EMP_DIR_001", "reportingManagerEmployeeId": "EMP_MGR_001"},
        {"employeeId": "EMP_DIR_002", "reportingManagerEmployeeId": "mgr_obj_id_123"},
    ])
    mock_db.employee_employment_histories.find.return_value = cursor_mock
    
    # Test manager identifiers
    identifiers = await get_manager_identifiers(mock_db, "EMP_MGR_001")
    assert "EMP_MGR_001" in identifiers
    assert "mgr_obj_id_123" in identifiers
    
    # Test reporting employee IDs
    reporting_ids = await get_reporting_employee_ids(mock_db, "EMP_MGR_001")
    assert "EMP_DIR_001" in reporting_ids
    assert "EMP_DIR_002" in reporting_ids
    assert len(reporting_ids) == 2

@pytest.mark.asyncio
async def test_approval_repository_scoped_query():
    mock_db = MagicMock()
    mgr_doc = {"_id": "mgr_obj_id_123", "employeeId": "EMP_MGR_001"}
    mock_db.employees.find.return_value = AsyncIter([mgr_doc])
    
    cursor_mock = MagicMock()
    cursor_mock.sort.return_value = cursor_mock
    cursor_mock.to_list = AsyncMock(return_value=[])
    
    mock_collection = MagicMock()
    mock_collection.find.return_value = cursor_mock
    mock_db.__getitem__.return_value = mock_collection
    
    repo = ApprovalRepository(mock_db)
    
    # Case 1: Filter without allowed_reporting_employee_ids (e.g. Super Admin)
    await repo.get_by_manager("EMP_MGR_001", allowed_reporting_employee_ids=None)
    call_args = mock_collection.find.call_args[0][0]
    assert "reportingManagerEmployeeId" in call_args
    assert set(call_args["reportingManagerEmployeeId"]["$in"]) == {"EMP_MGR_001", "mgr_obj_id_123"}
    assert "employeeId" not in call_args
    
    # Case 2: Filter with allowed_reporting_employee_ids (Regular Manager)
    allowed_ids = ["EMP_001", "EMP_002"]
    await repo.get_by_manager("EMP_MGR_001", allowed_reporting_employee_ids=allowed_ids)
    call_args2 = mock_collection.find.call_args[0][0]
    assert set(call_args2["reportingManagerEmployeeId"]["$in"]) == {"EMP_MGR_001", "mgr_obj_id_123"}
    assert call_args2["employeeId"] == {"$in": allowed_ids}

@pytest.mark.asyncio
async def test_approval_service_scoping():
    mock_db = MagicMock()
    service = ApprovalService(mock_db)
    service.repo = MagicMock()
    service.repo.get_by_manager = AsyncMock(return_value=[])
    service._enrich_approvals_with_employee_info = AsyncMock(return_value=[])
    
    # When service is called with allowed_reporting_employee_ids, it passes them to repository
    await service.get_manager_inbox("EMP_MGR_001", allowed_reporting_employee_ids=["EMP_A", "EMP_B"])
    service.repo.get_by_manager.assert_called_once_with("EMP_MGR_001", None, allowed_reporting_employee_ids=["EMP_A", "EMP_B"])
