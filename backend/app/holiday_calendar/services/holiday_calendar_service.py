from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional
from datetime import datetime
from app.holiday_calendar.repositories.holiday_calendar_repository import HolidayCalendarRepository, HolidayDateRepository
from app.holiday_calendar.schemas.holiday_calendar import HolidayCalendarCreate, HolidayCalendarUpdate, HolidayDateCreate, HolidayDateUpdate

class HolidayCalendarService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.calendar_repo = HolidayCalendarRepository(db)
        self.date_repo = HolidayDateRepository(db)
        self.db = db

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[dict]:
        return await self.calendar_repo.get_all(skip=skip, limit=limit)

    async def get_by_id(self, calendar_id: str) -> Optional[dict]:
        return await self.calendar_repo.get_by_id(calendar_id)

    async def create(self, data: HolidayCalendarCreate, current_user_id: str) -> dict:
        return await self.calendar_repo.create(data.model_dump(exclude_unset=True), created_by=current_user_id)

    async def update(self, calendar_id: str, data: HolidayCalendarUpdate, current_user_id: str) -> Optional[dict]:
        update_data = data.model_dump(exclude_unset=True)
        return await self.calendar_repo.update(calendar_id, update_data, updated_by=current_user_id)

    async def delete(self, calendar_id: str, current_user_id: str) -> bool:
        return await self.calendar_repo.soft_delete(calendar_id, deleted_by=current_user_id)

    # Dates management
    async def get_dates(self, calendar_id: str) -> List[dict]:
        cursor = self.date_repo.collection.find({"calendarId": calendar_id, "deletedAt": None, "status": "Active"}).sort([("holidayDate", 1)])
        docs = await cursor.to_list(length=None)
        return [self.date_repo._prepare_doc(doc) for doc in docs]

    async def add_date(self, calendar_id: str, data: HolidayDateCreate, current_user_id: str) -> dict:
        dump = data.model_dump(exclude_unset=True)
        dump["calendarId"] = calendar_id
        # ensure date is stored as datetime so mongo handles it well
        if "holidayDate" in dump and not isinstance(dump["holidayDate"], datetime):
            dump["holidayDate"] = datetime.combine(dump["holidayDate"], datetime.min.time())
        return await self.date_repo.create(dump, created_by=current_user_id)

    async def update_date(self, date_id: str, data: HolidayDateUpdate, current_user_id: str) -> Optional[dict]:
        dump = data.model_dump(exclude_unset=True)
        if "holidayDate" in dump and dump["holidayDate"] and not isinstance(dump["holidayDate"], datetime):
            dump["holidayDate"] = datetime.combine(dump["holidayDate"], datetime.min.time())
        return await self.date_repo.update(date_id, dump, updated_by=current_user_id)

    async def delete_date(self, date_id: str, current_user_id: str) -> bool:
        return await self.date_repo.soft_delete(date_id, deleted_by=current_user_id)
