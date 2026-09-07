import pytest
from datetime import datetime, timezone, timedelta
from app.main import app

from fastapi.testclient import TestClient
from app.dependencies import get_current_user
from app.db.mongo import get_database

from unittest.mock import AsyncMock, Mock

client = TestClient(app)

@pytest.fixture
def mock_db_monitor():
    class AsyncMockDB:
        def __init__(self):
            self.attendance_logs = AsyncMock()
            self.employees = AsyncMock()
    return AsyncMockDB()

def get_admin_user():
    return {
        "empId": "admin123",
        "employeeCode": "ADMIN1",
        "roles": ["HR_ADMIN"],
        "companyId": "comp-1"
    }

@pytest.mark.asyncio
def test_admin_punches_endpoint_success():
    mock_db = mock_db_monitor()
    
    app.dependency_overrides[get_database] = lambda: mock_db
    app.dependency_overrides[get_current_user] = get_admin_user

    mock_db.employees.find_one.return_value = {"employeeCode": "EMP1", "companyId": "comp-1"}
    
    mock_cursor = AsyncMock()
    mock_cursor.to_list.return_value = [
        {"punchType": "IN", "timestamp": datetime(2026, 9, 4, 9, 0, tzinfo=timezone.utc), "source": "MOBILE", "location": {"lat": 12.0, "lng": 77.0}},
        {"punchType": "OUT", "timestamp": datetime(2026, 9, 4, 18, 0, tzinfo=timezone.utc), "source": "ESSL"}
    ]
    mock_find_result = Mock()
    mock_find_result.sort.return_value = mock_cursor
    mock_db.attendance_logs.find = Mock(return_value=mock_find_result)

    response = client.get("/api/v2/attendance/monitor/EMP1/punches?date=2026-09-04&companyId=comp-1")
    
    assert response.status_code == 200
    data = response.json()
    assert data["empCode"] == "EMP1"
    assert len(data["punches"]) == 2
    assert data["punches"][0]["source"] == "MOBILE"
    assert data["punches"][0]["location"]["lat"] == 12.0
    assert data["punches"][1]["source"] == "ESSL"
    assert "location" not in data["punches"][1] or data["punches"][1].get("location") is None

    app.dependency_overrides.clear()

@pytest.mark.asyncio
def test_admin_punches_endpoint_isolation():
    mock_db = mock_db_monitor()
    
    app.dependency_overrides[get_database] = lambda: mock_db
    app.dependency_overrides[get_current_user] = get_admin_user

    # Mock employee find returning None
    mock_db.employees.find_one.return_value = None
    
    response = client.get("/api/v2/attendance/monitor/EMP2/punches?date=2026-09-04&companyId=comp-2")
    
    assert response.status_code == 403
    assert "unauthorized for your scope" in response.json()["detail"]

    app.dependency_overrides.clear()
