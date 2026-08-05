from motor.motor_asyncio import AsyncIOMotorDatabase
from app.employee.repositories.base_repository import BaseRepository
from app.holiday_calendar.models.holiday_calendar import HolidayCalendarModel, HolidayDateModel

class HolidayCalendarRepository(BaseRepository[HolidayCalendarModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "holiday_calendars", HolidayCalendarModel)

    async def get_all(self, skip: int = 0, limit: int = 100, filter_query: dict = None) -> dict:
        query = filter_query or {}
        query["deletedAt"] = None
        
        pipeline = [
            {"$match": query},
            {
                "$addFields": {
                    "branchObjId": {
                        "$cond": {
                            "if": {"$and": [{"$ne": ["$branchId", None]}, {"$ne": ["$branchId", ""]}]},
                            "then": {"$toObjectId": "$branchId"},
                            "else": None
                        }
                    },
                    "calendarIdStr": {"$toString": "$_id"}
                }
            },
            {
                "$lookup": {
                    "from": "branches",
                    "localField": "branchObjId",
                    "foreignField": "_id",
                    "as": "branchInfo"
                }
            },
            {
                "$unwind": {
                    "path": "$branchInfo",
                    "preserveNullAndEmptyArrays": True
                }
            },
            {
                "$lookup": {
                    "from": "holiday_dates",
                    "let": {"calId": "$calendarIdStr"},
                    "pipeline": [
                        {"$match": {"$expr": {"$eq": ["$calendarId", "$$calId"]}, "deletedAt": None}}
                    ],
                    "as": "dates"
                }
            },
            {
                "$addFields": {
                    "branchName": "$branchInfo.name",
                    "branchCode": "$branchInfo.code",
                    "holidayCount": {"$size": "$dates"}
                }
            },
            {"$sort": {"createdAt": -1}},
            {"$skip": skip},
            {"$limit": limit}
        ]
        
        cursor = self.collection.aggregate(pipeline)
        docs = await cursor.to_list(length=limit)
        
        total_count = await self.collection.count_documents(query)
        
        return {
            "data": [self._prepare_doc(doc) for doc in docs],
            "total": total_count,
            "page": (skip // limit) + 1 if limit > 0 else 1,
            "pageSize": limit,
            "totalPages": (total_count + limit - 1) // limit if limit > 0 else 1
        }

class HolidayDateRepository(BaseRepository[HolidayDateModel]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "holiday_dates", HolidayDateModel)
