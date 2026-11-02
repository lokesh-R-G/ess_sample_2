from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional
from datetime import datetime, timezone
from bson import ObjectId
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
        exists = await self.calendar_repo.collection.find_one({"holidayCalendarCode": data.holidayCalendarCode, "deletedAt": None})
        if exists:
            raise ValueError(f"Holiday Calendar with code {data.holidayCalendarCode} already exists.")
        return await self.calendar_repo.create(data.model_dump(exclude_unset=True), created_by=current_user_id)

    async def update(self, calendar_id: str, data: HolidayCalendarUpdate, current_user_id: str) -> Optional[dict]:
        """
        Updates a Holiday Calendar creating a new version (SCD-2) and synchronizes
        all active child holiday dates from the previous version to the new version's ObjectId.
        If branchId is modified on the calendar, synchronizes the branch's holidayCalendarCode.
        """
        async with await self.db.client.start_session() as session:
            async with session.start_transaction():
                # 1. Update calendar using repository
                updated_cal = await self.calendar_repo.update(
                    calendar_id, 
                    data.model_dump(exclude_unset=True), 
                    updated_by=current_user_id
                )
                if not updated_cal:
                    return None
                
                new_calendar_id = str(updated_cal.id if hasattr(updated_cal, 'id') else updated_cal.get('_id'))
                
                # 2. Synchronize child holiday dates if version changed (new ObjectId created)
                if new_calendar_id != str(calendar_id):
                    # Fetch active holiday dates from previous calendar version
                    prev_dates_cursor = self.date_repo.collection.find({
                        "calendarId": str(calendar_id),
                        "deletedAt": None,
                        "status": "Active"
                    }, session=session)
                    prev_dates = await prev_dates_cursor.to_list(length=None)
                    
                    now = datetime.now(timezone.utc)
                    for p_date in prev_dates:
                        # Check if a date with this holidayCode or date already exists on new calendar
                        exists_on_new = await self.date_repo.collection.find_one({
                            "calendarId": new_calendar_id,
                            "holidayDate": p_date["holidayDate"],
                            "deletedAt": None
                        }, session=session)
                        if exists_on_new:
                            continue
                            
                        new_date_doc = dict(p_date)
                        new_date_doc.pop("_id", None)
                        new_date_doc["calendarId"] = new_calendar_id
                        new_date_doc["createdAt"] = now
                        new_date_doc["updatedAt"] = now
                        new_date_doc["createdBy"] = current_user_id
                        new_date_doc["updatedBy"] = current_user_id
                        new_date_doc["version"] = 1
                        new_date_doc["isCurrent"] = True
                        new_date_doc["status"] = "Active"
                        
                        await self.date_repo.collection.insert_one(new_date_doc, session=session)

                # 3. Synchronize branch holidayCalendarCode if branchId is set
                target_branch_id = getattr(updated_cal, 'branchId', None) if not isinstance(updated_cal, dict) else updated_cal.get('branchId')
                cal_code = getattr(updated_cal, 'holidayCalendarCode', None) if not isinstance(updated_cal, dict) else updated_cal.get('holidayCalendarCode')
                if target_branch_id and cal_code:
                    try:
                        b_query = {"$or": [{"_id": ObjectId(target_branch_id)}, {"_id": target_branch_id}]}
                    except Exception:
                        b_query = {"_id": target_branch_id}
                    await self.db.branchs.update_one(
                        b_query,
                        {"$set": {"holidayCalendarCode": cal_code, "holidayCalendarId": new_calendar_id}},
                        session=session
                    )

                return updated_cal

    async def delete(self, calendar_id: str, current_user_id: str) -> bool:
        return await self.calendar_repo.soft_delete(calendar_id, deleted_by=current_user_id)

    async def get_history(self, code: str) -> List[dict]:
        cursor = self.calendar_repo.collection.find({"holidayCalendarCode": code, "deletedAt": None}).sort("version", -1)
        return [self.calendar_repo._format_doc(doc) async for doc in cursor]

    # Dates management
    async def get_dates(self, calendar_id: str) -> List[dict]:
        cursor = self.date_repo.collection.find({"calendarId": calendar_id, "deletedAt": None, "status": "Active"}).sort([("holidayDate", 1)])
        docs = await cursor.to_list(length=None)
        return [self.date_repo.model_class(**self.date_repo._prepare_doc(doc)) for doc in docs]

    async def add_date(self, calendar_id: str, data: HolidayDateCreate, current_user_id: str) -> dict:
        # Check if holiday with this code exists in this specific calendar
        exists = await self.date_repo.collection.find_one({
            "calendarId": calendar_id,
            "holidayCode": data.holidayCode, 
            "deletedAt": None
        })
        if exists:
            raise ValueError(f"Holiday with code {data.holidayCode} already exists in this calendar.")
        
        # Also check compound unique index condition (calendarId, holidayDate)
        h_date = data.holidayDate
        if isinstance(h_date, str):
            h_date = datetime.fromisoformat(h_date)
        if not isinstance(h_date, datetime):
            h_date = datetime.combine(h_date, datetime.min.time())
            
        date_exists = await self.date_repo.collection.find_one({
            "calendarId": calendar_id,
            "holidayDate": h_date,
            "deletedAt": None
        })
        if date_exists:
            raise ValueError(f"A holiday is already scheduled on {data.holidayDate} for this calendar.")

        dump = data.model_dump(exclude_unset=True)
        dump["calendarId"] = calendar_id
        dump["holidayDate"] = h_date
        return await self.date_repo.create(dump, created_by=current_user_id)

    async def update_date(self, date_id: str, data: HolidayDateUpdate, current_user_id: str) -> Optional[dict]:
        """
        Updates a holiday date in-place within the current calendar version to respect
        the unique compound index (calendarId, holidayDate).
        """
        dump = data.model_dump(exclude_unset=True)
        if "holidayDate" in dump and dump["holidayDate"]:
            if not isinstance(dump["holidayDate"], datetime):
                dump["holidayDate"] = datetime.combine(dump["holidayDate"], datetime.min.time())
                
        now = datetime.now(timezone.utc)
        dump["updatedAt"] = now
        dump["updatedBy"] = current_user_id
        
        try:
            obj_id = ObjectId(date_id)
        except Exception:
            return None
            
        res = await self.date_repo.collection.find_one_and_update(
            {"_id": obj_id, "deletedAt": None},
            {"$set": dump},
            return_document=True
        )
        if res:
            return self.date_repo.model_class(**self.date_repo._prepare_doc(res))
        return None

    async def delete_date(self, date_id: str, current_user_id: str) -> bool:
        return await self.date_repo.soft_delete(date_id, deleted_by=current_user_id)

    async def get_date_history(self, code: str) -> List[dict]:
        cursor = self.date_repo.collection.find({"holidayCode": code, "deletedAt": None}).sort("version", -1)
        docs = await cursor.to_list(length=None)
        return [self.date_repo.model_class(**self.date_repo._prepare_doc(doc)) for doc in docs]
