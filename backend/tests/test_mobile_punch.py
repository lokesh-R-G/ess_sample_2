import pytest
from datetime import datetime, timezone, timedelta
from app.attendance_v2.services.mobile_punch_service import MobilePunchService
import uuid

from unittest.mock import AsyncMock, Mock

@pytest.fixture
def mock_db():
    class AsyncMockDB:
        def __init__(self):
            self.attendance_logs = AsyncMock()
            self.attendance_dirty_queue = AsyncMock()
    return AsyncMockDB()

@pytest.mark.asyncio
async def test_mobile_punch_validation(mock_db):
    service = MobilePunchService(mock_db)
    
    # Missing clientEventId
    with pytest.raises(ValueError, match="clientEventId is required"):
        await service.register_punch("E01", "id-1", {"punchType": "IN", "occurredAt": "2026-09-04T10:00:00Z"})
        
    # Missing occurredAt
    with pytest.raises(ValueError, match="occurredAt is required"):
        await service.register_punch("E01", "id-1", {"punchType": "IN", "clientEventId": "evt1"})
        
    # Invalid occurredAt
    with pytest.raises(ValueError, match="occurredAt must be a valid ISO format date"):
        await service.register_punch("E01", "id-1", {"punchType": "IN", "clientEventId": "evt1", "occurredAt": "not-a-date"})

    # Invalid punch type
    with pytest.raises(ValueError, match="punchType must be IN or OUT"):
        await service.register_punch("E01", "id-1", {"punchType": "BREAK", "clientEventId": "evt1", "occurredAt": "2026-09-04T10:00:00Z"})

    # Invalid location
    with pytest.raises(ValueError, match="latitude must be between -90 and 90"):
        await service.register_punch("E01", "id-1", {
            "punchType": "IN", "clientEventId": "evt1", "occurredAt": "2026-09-04T10:00:00Z",
            "latitude": 91, "longitude": 0
        })

@pytest.mark.asyncio
async def test_mobile_punch_success(mock_db):
    service = MobilePunchService(mock_db)
    
    mock_db.attendance_logs.update_one.return_value = Mock(upserted_id="new_id")
    
    payload = {
        "punchType": "IN",
        "occurredAt": "2026-09-04T10:00:00Z",
        "clientEventId": "evt-123",
        "latitude": 12.34,
        "longitude": 56.78
    }
    
    res = await service.register_punch("E01", "uuid-1", payload)
    
    assert res["status"] == "SUCCESS"
    assert res["punchId"] == "new_id"
    assert res["isNew"] is True
    assert res["source"] == "MOBILE"
    
    # Check dirty queue push
    mock_db.attendance_dirty_queue.insert_one.assert_called_once()
    
    # Check attendance logs update
    mock_db.attendance_logs.update_one.assert_called_once()
    args, kwargs = mock_db.attendance_logs.update_one.call_args
    assert "fingerprint" in args[0]
    set_on_insert = args[1]["$setOnInsert"]
    assert set_on_insert["empId"] == "E01"
    assert set_on_insert["employeeId"] == "uuid-1"
    assert set_on_insert["source"] == "MOBILE"
    assert set_on_insert["punchType"] == "IN"
    assert "location" in set_on_insert
    assert set_on_insert["location"]["lat"] == 12.34

@pytest.mark.asyncio
async def test_mobile_punch_idempotent(mock_db):
    from pymongo.errors import DuplicateKeyError
    
    service = MobilePunchService(mock_db)
    
    # Simulate duplicate key error
    mock_db.attendance_logs.update_one.side_effect = DuplicateKeyError("dup")
    
    existing_doc = {
        "_id": "existing_id",
        "punchType": "IN",
        "timestamp": datetime.now(timezone.utc),
        "serverReceivedAt": datetime.now(timezone.utc),
        "source": "MOBILE"
    }
    mock_db.attendance_logs.find_one.return_value = existing_doc
    
    payload = {
        "punchType": "IN",
        "occurredAt": "2026-09-04T10:00:00Z",
        "clientEventId": "evt-123"
    }
    
    res = await service.register_punch("E01", "uuid-1", payload)
    
    assert res["status"] == "SUCCESS"
    assert res["punchId"] == "existing_id"
    assert res["isNew"] is False
    
    # Should not queue dirty queue again
    mock_db.attendance_dirty_queue.insert_one.assert_not_called()

@pytest.mark.asyncio
async def test_get_today_punches(mock_db):
    service = MobilePunchService(mock_db)
    
    mock_cursor = AsyncMock()
    # Mock to_list to return some punches
    mock_cursor.to_list.return_value = [
        {
            "_id": "punch1",
            "punchType": "IN",
            "timestamp": datetime.now(timezone.utc),
            "source": "MOBILE"
        },
        {
            "_id": "punch2",
            "punchType": "OUT",
            "timestamp": datetime.now(timezone.utc) + timedelta(hours=4),
            "source": "MOBILE"
        }
    ]
    # Chain the methods on find
    mock_find_result = Mock()
    mock_find_result.sort.return_value = mock_cursor
    # Instead of inheriting AsyncMock behavior, force find to be a regular Mock
    mock_db.attendance_logs.find = Mock(return_value=mock_find_result)
    
    res = await service.get_today_punches("E01")
    
    assert len(res) == 2
    assert res[0]["punchId"] == "punch1"
    assert res[0]["punchType"] == "IN"
    assert res[1]["punchId"] == "punch2"
    assert res[1]["punchType"] == "OUT"
    
    # Verify find was called with right arguments
    mock_db.attendance_logs.find.assert_called_once()
    args, kwargs = mock_db.attendance_logs.find.call_args
    query = args[0]
    assert query["empId"] == "E01"
    assert "$gte" in query["timestamp"]
    assert "$lt" in query["timestamp"]
