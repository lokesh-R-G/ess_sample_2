from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
from ..schemas.holiday import HolidayCreate, HolidayUpdate
from bson import ObjectId

class HolidayValidator:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["holidays"]
        
    async def validate_create(self, data: HolidayCreate):
        query = {"name": data.name, "deletedAt": None}
        if hasattr(data, 'companyId') and data.companyId:
            query["companyId"] = data.companyId
            parent = await self.db["companies"].find_one({"_id": ObjectId(data.companyId), "deletedAt": None})
            if not parent:
                raise HTTPException(status_code=400, detail="Parent company not found or archived")
        if await self.collection.find_one(query):
            raise HTTPException(status_code=409, detail=f"Holiday with this name already exists")
            
    async def validate_update(self, id: str, data: HolidayUpdate):
        pass # Optional update validation
