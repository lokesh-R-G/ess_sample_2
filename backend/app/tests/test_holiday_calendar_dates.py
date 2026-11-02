import pytest
import mongomock
import mongomock_motor
from datetime import datetime, timezone
from app.holiday_calendar.services.holiday_calendar_service import HolidayCalendarService
from app.holiday_calendar.schemas.holiday_calendar import HolidayCalendarCreate, HolidayCalendarUpdate

mongomock.ignore_feature('session')

@pytest.fixture
def mock_db():
    client = mongomock_motor.AsyncMongoMockClient()
    db = client["test_db"]
    class MockSession:
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass
        def start_transaction(self):
            return self
    async def mock_start_session(*args, **kwargs):
        return MockSession()
    client.start_session = mock_start_session
    return db

@pytest.mark.asyncio
async def test_holiday_calendar_effective_dates_persistence(mock_db):
    service = HolidayCalendarService(mock_db)
    eff_from = datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc)
    eff_to = datetime(2026, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
    
    # 1. Create calendar with both dates
    create_dto = HolidayCalendarCreate(
        holidayCalendarCode="CAL_2026",
        name="Calendar 2026",
        year=2026,
        effectiveFrom=eff_from,
        effectiveTo=eff_to
    )
    created = await service.create(create_dto, current_user_id="user1")
    assert created.effectiveFrom.replace(tzinfo=timezone.utc) == eff_from
    assert created.effectiveTo.replace(tzinfo=timezone.utc) == eff_to
    
    cal_id = created.id
    
    # 2. Verify get_by_id returns both dates
    fetched = await service.get_by_id(cal_id)
    assert fetched.effectiveFrom.replace(tzinfo=timezone.utc) == eff_from
    assert fetched.effectiveTo.replace(tzinfo=timezone.utc) == eff_to
    
    # 3. Update description only - verify effective dates are preserved
    update_dto = HolidayCalendarUpdate(
        description="Updated description"
    )
    updated = await service.update(cal_id, update_dto, current_user_id="user1")
    assert updated.description == "Updated description"
    assert updated.effectiveFrom.replace(tzinfo=timezone.utc) == eff_from
    assert updated.effectiveTo.replace(tzinfo=timezone.utc) == eff_to
    
    # 4. Update effectiveTo explicitly
    new_eff_to = datetime(2027, 1, 15, 0, 0, tzinfo=timezone.utc)
    update_dto2 = HolidayCalendarUpdate(
        effectiveTo=new_eff_to
    )
    updated2 = await service.update(updated.id, update_dto2, current_user_id="user1")
    assert updated2.effectiveTo.replace(tzinfo=timezone.utc) == new_eff_to
