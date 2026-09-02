import pytest
from unittest.mock import AsyncMock, MagicMock
from app.reimbursement.services.reimbursement_service import ReimbursementService

@pytest.fixture
def mock_db():
    db = MagicMock()
    return db

@pytest.mark.asyncio
async def test_reimbursement_resolver_boundaries(mock_db):
    service = ReimbursementService(mock_db)
    
    mock_cursor = AsyncMock()
    # Mocking V1 being returned correctly based on query.
    mock_cursor.to_list.return_value = [
        {
            "_id": "v1_id",
            "companyId": "COMP1",
            "policyCode": "TRIP_ALL_DEFAULT",
            "ratePerKm": 10.0,
            "version": 1,
            "effectiveFrom": "2026-07-01",
            "effectiveTo": "2026-08-01",
            "isCurrent": False,
            "allowedTripTypes": ["One Way"]
        }
    ]
    
    mock_find_result = MagicMock()
    mock_find_result.sort = MagicMock(return_value=mock_cursor)
    mock_db.trip_allowance_policies.find = MagicMock(return_value=mock_find_result)
    
    # Simulating a July trip processed in December.
    trip_date = "2026-07-15"
    policy = await service.get_active_trip_allowance("COMP1", trip_date)
    
    assert policy.version == 1
    assert policy.ratePerKm == 10.0
    
    # Verify the exact query structure ensures no overlaps
    call_args = mock_db.trip_allowance_policies.find.call_args[0][0]
    assert call_args["companyId"] == "COMP1"
    assert call_args["policyCode"] == "TRIP_ALL_DEFAULT"
    assert call_args["effectiveFrom"] == {"$lte": trip_date}
    assert "$or" in call_args
    assert {"effectiveTo": None} in call_args["$or"]
    assert {"effectiveTo": {"$gt": trip_date}} in call_args["$or"]
